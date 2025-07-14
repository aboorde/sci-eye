# 🏗️ Architecture Evolution Plan

## Current Architecture (MVP)
```
┌─────────────────┐
│   User Runs     │
│ pharma_news.py  │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Fetch  │
    │   RSS   │
    └────┬────┘
         │
    ┌────▼────┐
    │Classify │
    │ (OpenAI)│
    └────┬────┘
         │
    ┌────▼────┐
    │ Scrape  │
    │  Article│
    └────┬────┘
         │
    ┌────▼────┐
    │   Save  │
    │  JSON   │
    └────┬────┘
         │
    ┌────▼────────┐
    │   Static    │
    │  Dashboard  │
    └─────────────┘
```

**Limitations:**
- Manual execution required
- No real-time updates
- Limited scalability
- No user management
- Single point of failure

## Target Architecture (Enterprise-Ready)
```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (AWS ALB)              │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
     ┌────────▼────────┐         ┌────────▼────────┐
     │   Web App       │         │    API Gateway   │
     │  (SvelteKit)    │         │   (GraphQL)      │
     └────────┬────────┘         └────────┬────────┘
              │                           │
              └────────────┬──────────────┘
                          │
                ┌─────────▼──────────┐
                │   Redis Cache      │
                │  (ElastiCache)     │
                └─────────┬──────────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼─────┐    ┌─────────▼────────┐   ┌──────▼──────┐
│  Auth    │    │   App Servers     │   │  Workers    │
│ Service  │    │   (ECS Fargate)   │   │  (SQS+Lambda)│
└────┬─────┘    └─────────┬────────┘   └──────┬──────┘
     │                    │                    │
     └────────────────────┼────────────────────┘
                          │
                ┌─────────▼──────────┐
                │    PostgreSQL      │
                │  (RDS Multi-AZ)    │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │   TimescaleDB      │
                │  (Time Series)     │
                └────────────────────┘

External Services:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   OpenAI    │  │  SendGrid   │  │   Twilio    │
│     API     │  │   (Email)   │  │    (SMS)    │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Migration Path (6 Phases)

### Phase 1: Database Foundation (Week 1-2)
```python
# 1. Set up PostgreSQL with proper schema
# 2. Migrate JSON data to PostgreSQL
# 3. Add database abstraction layer

class DatabaseManager:
    def __init__(self):
        self.pool = asyncpg.create_pool(DATABASE_URL)
    
    async def insert_article(self, article: Dict) -> str:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                INSERT INTO articles (
                    id, title, link, content, topics, 
                    confidence_scores, source_feed, 
                    date_published, date_processed
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """, 
            article['id'], article['title'], article['link'],
            article['content'], article['topics'], 
            Json(article['confidence_scores']), article['source_feed'],
            article['date_published'], article['date_processed']
        )
```

### Phase 2: Queue System (Week 3-4)
```python
# Implement job queue for async processing
from celery import Celery
from kombu import Queue

app = Celery('pharma_monitor')
app.conf.task_routes = {
    'tasks.classify_article': {'queue': 'classification'},
    'tasks.scrape_article': {'queue': 'scraping'},
    'tasks.send_alert': {'queue': 'alerts'},
}

@app.task(bind=True, max_retries=3)
def process_article(self, article_data):
    try:
        # Classification
        topics = classify_article(article_data)
        if not topics:
            return None
            
        # Scraping
        content = scrape_article.delay(article_data['link'])
        
        # Alert checking
        check_alerts.delay(article_data['id'])
        
        return article_data
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

### Phase 3: API Development (Week 5-6)
```javascript
// GraphQL Schema
type Article {
  id: ID!
  title: String!
  summary: String!
  topics: [Topic!]!
  confidenceScores: JSON!
  datePublished: DateTime!
  source: Source!
  alerts: [Alert!]
}

type Query {
  articles(
    filter: ArticleFilter
    sort: ArticleSort
    pagination: PaginationInput
  ): ArticleConnection!
  
  articleById(id: ID!): Article
  
  searchArticles(
    query: String!
    filters: SearchFilters
  ): SearchResults!
}

type Mutation {
  createAlertRule(input: AlertRuleInput!): AlertRule!
  updateAlertRule(id: ID!, input: AlertRuleInput!): AlertRule!
  deleteAlertRule(id: ID!): Boolean!
}

type Subscription {
  articleAdded(topics: [String!]): Article!
  alertTriggered(userId: ID!): Alert!
}
```

### Phase 4: Real-time Infrastructure (Week 7-8)
```typescript
// WebSocket server for real-time updates
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';

class RealtimeServer {
  constructor(httpServer) {
    this.io = new Server(httpServer, {
      cors: { origin: process.env.FRONTEND_URL }
    });
    
    // Redis adapter for horizontal scaling
    const pubClient = redis.createClient({ url: REDIS_URL });
    const subClient = pubClient.duplicate();
    this.io.adapter(createAdapter(pubClient, subClient));
    
    this.setupEventHandlers();
  }
  
  setupEventHandlers() {
    this.io.on('connection', (socket) => {
      // Join user-specific room
      socket.on('authenticate', async (token) => {
        const userId = await validateToken(token);
        socket.join(`user:${userId}`);
        
        // Subscribe to user's alert topics
        const userTopics = await getUserTopics(userId);
        userTopics.forEach(topic => {
          socket.join(`topic:${topic}`);
        });
      });
    });
  }
  
  // Emit new article to relevant users
  async broadcastArticle(article) {
    // Emit to topic rooms
    article.topics.forEach(topic => {
      this.io.to(`topic:${topic}`).emit('article:new', article);
    });
    
    // Emit to users with matching alerts
    const matchingUsers = await getMatchingUsers(article);
    matchingUsers.forEach(userId => {
      this.io.to(`user:${userId}`).emit('alert:triggered', {
        article,
        triggeredAt: new Date()
      });
    });
  }
}
```

### Phase 5: Scalability Features (Week 9-10)
```yaml
# Kubernetes deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pharma-monitor-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pharma-monitor-api
  template:
    metadata:
      labels:
        app: pharma-monitor-api
    spec:
      containers:
      - name: api
        image: pharma-monitor:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pharma-monitor-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pharma-monitor-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Phase 6: Enterprise Features (Week 11-12)
- Multi-tenancy support
- SSO integration (SAML/OAuth)
- Advanced analytics pipeline
- Compliance logging
- Disaster recovery

## Cost Analysis

### Current Costs (Monthly)
- OpenAI API: ~$50
- Hosting: $0 (local)
- Total: $50

### Target Architecture Costs (Monthly)
- AWS Infrastructure: ~$2,500
  - RDS PostgreSQL: $400
  - ECS Fargate: $800
  - ElastiCache: $200
  - ALB: $25
  - S3/CloudFront: $100
  - Lambda: $200
  - Other services: $775
- OpenAI API: ~$500 (with caching)
- SendGrid: $80
- Monitoring (Datadog): $200
- Total: ~$3,280

### Revenue Projection
- 100 Starter customers: $29,900
- 20 Professional customers: $19,980
- 5 Enterprise customers: $25,000+
- Total MRR: $74,880
- Gross Margin: 95%+

## Key Benefits of New Architecture

1. **Scalability**: Handle 1M+ articles/day
2. **Reliability**: 99.9% uptime SLA
3. **Performance**: <100ms API response time
4. **Security**: SOC 2 compliant
5. **Flexibility**: Easy to add new features
6. **Cost-Effective**: Scales with usage

The investment in proper architecture will pay for itself within 2 months of launch!