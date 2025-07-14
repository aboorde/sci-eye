# 🔔 Quick Win: Real-Time Alert System Implementation

## Why This First?
- **Immediate Value**: Users can act on news within minutes, not hours
- **Low Implementation Cost**: Builds on existing classification system  
- **High Engagement**: Brings users back multiple times per day
- **Revenue Driver**: Premium feature users will pay for

## Implementation Plan (2 weeks)

### Week 1: Backend Infrastructure

#### Day 1-2: Database Schema
```sql
-- Alert rules table
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    conditions JSONB NOT NULL, -- {"topics": ["FDA Approval"], "companies": ["Pfizer"], "confidence": 1.0}
    channels JSONB NOT NULL, -- {"email": true, "slack": "webhook_url", "sms": "+1234567890"}
    severity ENUM('critical', 'high', 'medium', 'low'),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alert history
CREATE TABLE alert_history (
    id UUID PRIMARY KEY,
    rule_id UUID REFERENCES alert_rules(id),
    article_id VARCHAR(255) NOT NULL,
    triggered_at TIMESTAMP DEFAULT NOW(),
    delivered_channels JSONB,
    delivery_status JSONB
);

-- User notification preferences
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50),
    daily_limit INTEGER DEFAULT 50,
    critical_override_quiet BOOLEAN DEFAULT true
);
```

#### Day 3-4: Alert Engine
```python
# alert_engine.py
import asyncio
from typing import List, Dict
import aioredis
from sendgrid import SendGridAPIClient
from twilio.rest import Client
import httpx

class AlertEngine:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost")
        self.sendgrid = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.twilio = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        
    async def process_article(self, article: Dict):
        """Check article against all active alert rules"""
        matching_rules = await self.find_matching_rules(article)
        
        for rule in matching_rules:
            if await self.should_send_alert(rule, article):
                await self.send_alert(rule, article)
                
    async def find_matching_rules(self, article: Dict) -> List[Dict]:
        """Find all rules that match this article"""
        rules = await db.fetch("""
            SELECT * FROM alert_rules 
            WHERE active = true
            AND (
                conditions->>'topics' ?| $1
                OR conditions->>'companies' ?| $2
                OR conditions->>'keywords' ?| $3
            )
        """, article['topics'], article.get('companies', []), article.get('keywords', []))
        
        return [rule for rule in rules if self.matches_conditions(rule, article)]
        
    async def send_alert(self, rule: Dict, article: Dict):
        """Send alert through configured channels"""
        tasks = []
        
        if rule['channels'].get('email'):
            tasks.append(self.send_email_alert(rule, article))
            
        if rule['channels'].get('sms'):
            tasks.append(self.send_sms_alert(rule, article))
            
        if rule['channels'].get('slack'):
            tasks.append(self.send_slack_alert(rule, article))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log delivery status
        await self.log_alert_delivery(rule, article, results)
```

#### Day 5: Integration with Monitor
```python
# Modified pharma_news_monitor.py
class PharmaNewsMonitor:
    def __init__(self, api_key: str):
        # ... existing code ...
        self.alert_engine = AlertEngine() if ALERTS_ENABLED else None
        
    async def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles with alert checking"""
        # ... existing classification code ...
        
        # After classification, check alerts
        if self.alert_engine and classified_articles:
            alert_tasks = [
                self.alert_engine.process_article(article)
                for article in classified_articles
            ]
            await asyncio.gather(*alert_tasks)
            
        return processed_articles
```

### Week 2: Frontend & Polish

#### Day 6-7: Alert Configuration UI
```svelte
<!-- src/routes/alerts/+page.svelte -->
<script>
  import { Plus, Bell, Filter, Zap } from 'lucide-svelte';
  import AlertRuleCard from '$lib/components/alerts/AlertRuleCard.svelte';
  import CreateAlertModal from '$lib/components/alerts/CreateAlertModal.svelte';
  
  let showCreateModal = false;
  let alertRules = [];
  
  onMount(async () => {
    alertRules = await fetch('/api/alerts').then(r => r.json());
  });
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <div>
      <h1 class="text-3xl font-bold mb-2">Alert Rules</h1>
      <p class="text-base-content/60">
        Get notified instantly when news matches your criteria
      </p>
    </div>
    
    <button 
      class="btn btn-primary gap-2"
      on:click={() => showCreateModal = true}
    >
      <Plus size={16} />
      Create Alert
    </button>
  </div>
  
  <!-- Alert Stats -->
  <div class="stats stats-horizontal shadow">
    <div class="stat">
      <div class="stat-figure text-primary">
        <Bell size={24} />
      </div>
      <div class="stat-title">Active Alerts</div>
      <div class="stat-value">{alertRules.filter(r => r.active).length}</div>
    </div>
    
    <div class="stat">
      <div class="stat-figure text-secondary">
        <Zap size={24} />
      </div>
      <div class="stat-title">Triggered Today</div>
      <div class="stat-value">12</div>
    </div>
  </div>
  
  <!-- Alert Rules Grid -->
  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
    {#each alertRules as rule}
      <AlertRuleCard {rule} on:edit on:delete />
    {/each}
  </div>
</div>

{#if showCreateModal}
  <CreateAlertModal on:close={() => showCreateModal = false} />
{/if}
```

#### Day 8-9: Alert Builder Component
```svelte
<!-- CreateAlertModal.svelte -->
<script>
  let alertRule = {
    name: '',
    conditions: {
      topics: [],
      companies: [],
      keywords: [],
      confidence: 0.85,
      allRequired: false
    },
    channels: {
      email: true,
      browser: true,
      slack: false,
      sms: false
    },
    severity: 'medium'
  };
  
  // Visual rule builder
  let conditionBuilder = {
    mode: 'simple', // or 'advanced'
    simpleRules: []
  };
</script>

<div class="modal-box max-w-3xl">
  <h3 class="font-bold text-lg mb-4">Create Alert Rule</h3>
  
  <!-- Step 1: Name & Description -->
  <div class="form-control">
    <label class="label">Alert Name</label>
    <input 
      type="text" 
      class="input input-bordered"
      placeholder="e.g., Competitor FDA Approvals"
      bind:value={alertRule.name}
    />
  </div>
  
  <!-- Step 2: Conditions Builder -->
  <div class="divider">When these conditions are met</div>
  
  <div class="space-y-4">
    <!-- Topic Selection -->
    <div class="form-control">
      <label class="label">Topics</label>
      <select 
        multiple 
        class="select select-bordered h-32"
        bind:value={alertRule.conditions.topics}
      >
        {#each availableTopics as topic}
          <option value={topic}>{topic}</option>
        {/each}
      </select>
    </div>
    
    <!-- Company Watchlist -->
    <div class="form-control">
      <label class="label">Companies to Monitor</label>
      <TagInput 
        placeholder="Type company names..."
        bind:tags={alertRule.conditions.companies}
      />
    </div>
    
    <!-- Keywords -->
    <div class="form-control">
      <label class="label">Keywords</label>
      <TagInput 
        placeholder="Add keywords..."
        bind:tags={alertRule.conditions.keywords}
      />
    </div>
    
    <!-- Confidence Threshold -->
    <div class="form-control">
      <label class="label">
        Minimum Confidence: {alertRule.conditions.confidence * 100}%
      </label>
      <input 
        type="range" 
        min="0.7" 
        max="1" 
        step="0.05"
        class="range range-primary"
        bind:value={alertRule.conditions.confidence}
      />
    </div>
  </div>
  
  <!-- Step 3: Delivery Channels -->
  <div class="divider">Notify me via</div>
  
  <div class="grid grid-cols-2 gap-4">
    <label class="flex items-center gap-2 cursor-pointer">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary"
        bind:checked={alertRule.channels.email}
      />
      <span>Email</span>
    </label>
    
    <label class="flex items-center gap-2 cursor-pointer">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary"
        bind:checked={alertRule.channels.browser}
      />
      <span>Browser Push</span>
    </label>
    
    <label class="flex items-center gap-2 cursor-pointer">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary"
        bind:checked={alertRule.channels.slack}
      />
      <span>Slack</span>
    </label>
    
    <label class="flex items-center gap-2 cursor-pointer">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary"
        bind:checked={alertRule.channels.sms}
      />
      <span>SMS (Premium)</span>
    </label>
  </div>
  
  <!-- Preview -->
  <div class="alert alert-info mt-6">
    <span>
      This alert will trigger when articles match 
      {#if alertRule.conditions.allRequired}ALL{:else}ANY{/if} of your conditions
    </span>
  </div>
  
  <div class="modal-action">
    <button class="btn" on:click={() => dispatch('close')}>Cancel</button>
    <button class="btn btn-primary" on:click={createAlert}>Create Alert</button>
  </div>
</div>
```

#### Day 10: Real-time Updates
```javascript
// src/lib/services/websocket.js
import { writable } from 'svelte/store';

export const notifications = writable([]);

class AlertWebSocket {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
  }
  
  connect() {
    this.ws = new WebSocket(import.meta.env.VITE_WS_URL);
    
    this.ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      
      // Add to notifications store
      notifications.update(n => [alert, ...n].slice(0, 50));
      
      // Show browser notification if permitted
      if (Notification.permission === 'granted') {
        new Notification(alert.title, {
          body: alert.summary,
          icon: '/logo.png',
          badge: '/badge.png',
          tag: alert.id,
          renotify: true,
          actions: [
            { action: 'view', title: 'View Article' },
            { action: 'dismiss', title: 'Dismiss' }
          ]
        });
      }
      
      // Play sound for critical alerts
      if (alert.severity === 'critical') {
        new Audio('/alert-sound.mp3').play();
      }
    };
    
    this.ws.onerror = () => this.reconnect();
    this.ws.onclose = () => this.reconnect();
  }
  
  reconnect() {
    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, Math.min(1000 * this.reconnectAttempts, 30000));
  }
}

export const alertSocket = new AlertWebSocket();
```

### Immediate User Benefits:

1. **Never Miss Critical News**: FDA approvals, trial failures, M&A announcements
2. **Competitive Edge**: React to news before markets open
3. **Reduced Noise**: Only get alerted for truly relevant news
4. **Team Coordination**: Share alert rules across departments
5. **Compliance**: Audit trail of who was notified when

### Revenue Impact:
- Basic: 5 alerts/month (Free tier)
- Pro: Unlimited alerts + SMS ($50/month addon)
- Enterprise: Team alerts + webhook API (Custom pricing)

This single feature could drive 40% conversion from free to paid!