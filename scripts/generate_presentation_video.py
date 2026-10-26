import os
import sys
import base64
import subprocess
import time
from xml.sax.saxutils import escape

TOTAL_SLIDES = 14
OUTPUT_DIR = "/tmp/bloodbridge_video"
FINAL_VIDEO = "/Users/pranayreddyn/Code/untitled folder/bloodbridge/demo/presentation.mp4"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FINAL_VIDEO), exist_ok=True)

# Load screenshot for Slide 7
screenshot_path = "/Users/pranayreddyn/Code/untitled folder/bloodbridge/demo/screenshots/ci-cd-pipeline-run.png"
if os.path.exists(screenshot_path):
    with open(screenshot_path, "rb") as f:
        SCREENSHOT_B64 = base64.b64encode(f.read()).decode("utf-8")
else:
    SCREENSHOT_B64 = ""

def base_slide(num, title, subtitle, content_svg):
    progress_w = int(1920 * (num / TOTAL_SLIDES))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="50%" stop-color="#0E1726"/>
      <stop offset="100%" stop-color="#060911"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#162238"/>
      <stop offset="100%" stop-color="#0E182A"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#EF4444"/>
      <stop offset="100%" stop-color="#F59E0B"/>
    </linearGradient>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#34D399"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1920" height="1080" fill="url(#bg)"/>

  <!-- Top Bar -->
  <rect x="0" y="0" width="1920" height="84" fill="#090E1A" fill-opacity="0.95"/>
  <line x1="0" y1="84" x2="1920" y2="84" stroke="#1E293B" stroke-width="2"/>

  <!-- Brand -->
  <circle cx="80" cy="42" r="13" fill="#EF4444"/>
  <text x="106" y="50" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">BloodBridge</text>
  <rect x="260" y="26" width="170" height="32" rx="16" fill="#1E293B"/>
  <text x="345" y="48" fill="#94A3B8" font-size="13" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">DEVOPS CAPSTONE</text>

  <!-- Author & Counter -->
  <text x="1590" y="50" fill="#E2E8F0" font-size="16" font-family="-apple-system, Arial, sans-serif">Pranay Reddy N</text>
  <rect x="1740" y="26" width="120" height="32" rx="16" fill="#EF4444" fill-opacity="0.2"/>
  <text x="1800" y="48" fill="#FCA5A5" font-size="14" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Slide {num} / {TOTAL_SLIDES}</text>

  <!-- Header -->
  <text x="120" y="145" fill="#FFFFFF" font-size="44" font-weight="800" font-family="-apple-system, Arial, sans-serif">{escape(title)}</text>
  <text x="120" y="185" fill="#94A3B8" font-size="22" font-weight="400" font-family="-apple-system, Arial, sans-serif">{escape(subtitle)}</text>

  <!-- Main Slide Content Area -->
  {content_svg}

  <!-- Footer Progress Bar -->
  <rect x="0" y="1072" width="1920" height="8" fill="#1E293B"/>
  <rect x="0" y="1072" width="{progress_w}" height="8" fill="#EF4444"/>
</svg>'''

slides_data = []

# ==========================================
# SLIDE 1: Title & Capstone Overview
# ==========================================
s1_content = '''
  <rect x="120" y="220" width="1680" height="780" rx="20" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="2"/>
  
  <text x="960" y="360" fill="#FFFFFF" font-size="68" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">BloodBridge</text>
  <rect x="760" y="385" width="400" height="6" rx="3" fill="url(#accentGrad)"/>
  
  <text x="960" y="450" fill="#E2E8F0" font-size="28" font-weight="500" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Blood Donor Registry, Inventory &amp; Hospital Request Fulfilment</text>
  <text x="960" y="495" fill="#94A3B8" font-size="22" font-weight="400" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Shipped Through a Full DevSecOps Pipeline to Amazon EKS</text>

  <g transform="translate(180, 560)">
    <rect x="0" y="0" width="350" height="180" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="175" y="45" fill="#60A5FA" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">KUBERNETES &amp; GITOPS</text>
    <text x="175" y="85" fill="#F8FAFC" font-size="24" font-weight="600" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Amazon EKS 1.34</text>
    <text x="175" y="125" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Argo CD · Helm 3 · Traefik</text>

    <rect x="390" y="0" width="350" height="180" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="565" y="45" fill="#34D399" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">SECURITY &amp; CI/CD</text>
    <text x="565" y="85" fill="#F8FAFC" font-size="24" font-weight="600" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">GitHub Actions</text>
    <text x="565" y="125" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Trivy Scans · SBOM · Non-root</text>

    <rect x="780" y="0" width="350" height="180" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="955" y="45" fill="#F472B6" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">INFRASTRUCTURE AS CODE</text>
    <text x="955" y="85" fill="#F8FAFC" font-size="24" font-weight="600" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Terraform</text>
    <text x="955" y="125" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Multi-AZ VPC · EKS Node Groups</text>

    <rect x="1170" y="0" width="350" height="180" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="1345" y="45" fill="#FBBF24" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">OBSERVABILITY</text>
    <text x="1345" y="85" fill="#F8FAFC" font-size="24" font-weight="600" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Prometheus &amp; Grafana</text>
    <text x="1345" y="125" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Golden Signals · Alertmanager</text>
  </g>

  <text x="960" y="850" fill="#64748B" font-size="18" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">github.com/pranay-reddy2/BloodBridge · Capstone October 2026</text>
'''
s1_audio = ("Hello everyone, and welcome to this capstone demonstration. My name is Pranay Reddy N, and "
            "today I am presenting BloodBridge. BloodBridge is a mission-critical blood donor registry, inventory tracking, "
            "and hospital request fulfilment platform. More importantly, it serves as the production payload for a complete, "
            "enterprise-grade DevSecOps pipeline deployed to Amazon EKS, governed by Argo CD GitOps, and fully observed with "
            "Prometheus and Grafana. Over the next several minutes, we will explore the domain problem, our architectural design, "
            "automated CI/CD security gates, infrastructure as code, and production reliability drills.")
slides_data.append((1, "BloodBridge DevSecOps Capstone", "Automated Blood Supply Chain on AWS EKS", s1_content, s1_audio))

# ==========================================
# SLIDE 2: The Core Problem
# ==========================================
s2_content = '''
  <g transform="translate(120, 220)">
    <!-- Problem 1 -->
    <rect x="0" y="0" width="850" height="230" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <circle cx="50" cy="50" r="20" fill="#EF4444" fill-opacity="0.2"/>
    <text x="50" y="57" fill="#EF4444" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">1</text>
    <text x="90" y="55" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Platelets Expire in 5 Days</text>
    <text x="90" y="95" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">Platelet products have a biological shelf life of only 5 days. Units are needlessly</text>
    <text x="90" y="125" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">lost and wasted when blood banks lack automated First-Expiring-First-Out stock rotation.</text>
    <text x="90" y="170" fill="#F87171" font-size="16" font-weight="600" font-family="-apple-system, Arial, sans-serif">Solution: Algorithmic FEFO queue issuance across all inventory</text>

    <!-- Problem 2 -->
    <rect x="0" y="260" width="850" height="230" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <circle cx="50" cy="310" r="20" fill="#F59E0B" fill-opacity="0.2"/>
    <text x="50" y="317" fill="#F59E0B" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">2</text>
    <text x="90" y="315" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">O-Negative Scarcity &amp; Misallocation</text>
    <text x="90" y="355" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">O-negative is universal, but accounts for only ~1% of donors. Too often, it is expended</text>
    <text x="90" y="385" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">for routine procedures when an alternative compatible blood group was available.</text>
    <text x="90" y="430" fill="#FBBF24" font-size="16" font-weight="600" font-family="-apple-system, Arial, sans-serif">Solution: Compatibility rules prioritize non-O- units first, reserving O- for emergencies</text>

    <!-- Problem 3 -->
    <rect x="0" y="520" width="850" height="230" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <circle cx="50" cy="570" r="20" fill="#3B82F6" fill-opacity="0.2"/>
    <text x="50" y="577" fill="#3B82F6" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">3</text>
    <text x="90" y="575" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Emergency Requests vs Manual Logs</text>
    <text x="90" y="615" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">Critical trauma requests compete with routine elective orders inside phone calls and</text>
    <text x="90" y="645" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">manual spreadsheets without triage ranking or concurrency protection.</text>
    <text x="90" y="690" fill="#60A5FA" font-size="16" font-weight="600" font-family="-apple-system, Arial, sans-serif">Solution: Urgency triage queue backed by SELECT FOR UPDATE SKIP LOCKED</text>
  </g>

  <!-- Metrics Grid -->
  <g transform="translate(1010, 220)">
    <rect x="0" y="0" width="370" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="185" y="130" fill="#EF4444" font-size="80" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">8</text>
    <text x="185" y="190" fill="#FFFFFF" font-size="22" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Blood Groups</text>
    <text x="185" y="230" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Matched by complete ABO/Rh</text>
    <text x="185" y="255" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">compatibility matrix</text>

    <rect x="410" y="0" width="370" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="595" y="130" fill="#F59E0B" font-size="70" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">5 Days</text>
    <text x="595" y="190" fill="#FFFFFF" font-size="22" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Platelet Shelf Life</text>
    <text x="595" y="230" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Tracked per individual unit with</text>
    <text x="595" y="255" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">daily Kubernetes CronJob sweep</text>

    <rect x="0" y="400" width="370" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="185" y="530" fill="#10B981" font-size="80" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">18</text>
    <text x="185" y="590" fill="#FFFFFF" font-size="22" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">REST Endpoints</text>
    <text x="185" y="630" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">FastAPI async services with</text>
    <text x="185" y="655" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Pydantic validation schemas</text>

    <rect x="410" y="400" width="370" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="595" y="530" fill="#3B82F6" font-size="80" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">40</text>
    <text x="595" y="590" fill="#FFFFFF" font-size="22" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Automated Tests</text>
    <text x="595" y="630" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Pytest test suite achieving</text>
    <text x="595" y="655" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">96% code coverage in CI</text>
  </g>
'''
s2_audio = ("Why does a blood bank urgently need better software? Blood products have strict biological lifespans. "
            "Platelets, for example, expire in only five days. Without strict First-Expiring-First-Out stock rotation, critical units "
            "are needlessly lost on storage shelves. Second, O-negative is the universal donor, yet represents only one percent of donors. "
            "Too often, it is expended when a patient could have safely received another compatible group. Finally, critical hospital requests "
            "compete with routine orders inside spreadsheets and telephone calls. BloodBridge solves this by algorithmically matching ABO and Rh "
            "compatibility, preserving O-negative stock for genuine emergencies, and tracking every single unit across eighteen production endpoints "
            "backed by forty automated tests.")
slides_data.append((2, "Why a Blood Bank Needs Better Software", "Domain Challenges: Shelf Life, Rarity, and Urgent Demand", s2_content, s2_audio))

# ==========================================
# SLIDE 3: Application Features
# ==========================================
s3_content = '''
  <g transform="translate(120, 220)">
    <!-- Row 1 -->
    <rect x="0" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="60" fill="#EF4444" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">01 · REGISTRY</text>
    <text x="40" y="105" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Donor Registry</text>
    <text x="40" y="150" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Search donors by blood group and city</text>
    <text x="40" y="185" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• 90-day eligibility automatically calculated</text>
    <text x="40" y="220" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Contact info &amp; donation history log</text>
    <text x="40" y="270" fill="#60A5FA" font-size="16" font-family="-apple-system, Arial, sans-serif">Prevents donor health over-extraction</text>

    <rect x="575" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="615" y="60" fill="#F59E0B" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">02 · DONATIONS</text>
    <text x="615" y="105" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Donation to Units</text>
    <text x="615" y="150" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Whole blood, plasma, or platelets</text>
    <text x="615" y="185" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Shelf life assigned: 5 to 365 days</text>
    <text x="615" y="220" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Unique unit tracking identifier</text>
    <text x="615" y="270" fill="#FBBF24" font-size="16" font-family="-apple-system, Arial, sans-serif">Exact biological tracking per bag</text>

    <rect x="1150" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1190" y="60" fill="#10B981" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">03 · INVENTORY</text>
    <text x="1190" y="105" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Inventory Control</text>
    <text x="1190" y="150" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Unit statuses: Available, Quarantined, Discarded</text>
    <text x="1190" y="185" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Daily Kubernetes CronJob expires stale stock</text>
    <text x="1190" y="220" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Real-time stock counts by ABO/Rh group</text>
    <text x="1190" y="270" fill="#34D399" font-size="16" font-family="-apple-system, Arial, sans-serif">Zero human error in shelf expiry</text>

    <!-- Row 2 -->
    <rect x="0" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="460" fill="#EC4899" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">04 · TRIAGE</text>
    <text x="40" y="505" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Hospital Requests</text>
    <text x="40" y="550" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Priority queues: Critical → Emergency → Routine</text>
    <text x="40" y="585" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Secondary ordering by request age</text>
    <text x="40" y="620" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Full hospital identity &amp; ward attribution</text>
    <text x="40" y="670" fill="#F472B6" font-size="16" font-family="-apple-system, Arial, sans-serif">Ensures critical patients receive priority</text>

    <rect x="575" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="615" y="460" fill="#6366F1" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">05 · FULFILMENT</text>
    <text x="615" y="505" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Smart Fulfilment</text>
    <text x="615" y="550" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• First-Expiring-First-Out allocation</text>
    <text x="615" y="585" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• Conservative O- conservation strategy</text>
    <text x="615" y="620" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• SELECT FOR UPDATE SKIP LOCKED locks</text>
    <text x="615" y="670" fill="#818CF8" font-size="16" font-family="-apple-system, Arial, sans-serif">Zero race conditions, zero wasted stock</text>

    <rect x="1150" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1190" y="460" fill="#3B82F6" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">06 · OPERATIONS</text>
    <text x="1190" y="505" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Production Ops APIs</text>
    <text x="1190" y="550" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• /health: liveness verification</text>
    <text x="1190" y="585" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• /ready: active PostgreSQL DB connection check</text>
    <text x="1190" y="620" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">• /metrics: Prometheus scraper endpoint</text>
    <text x="1190" y="670" fill="#60A5FA" font-size="16" font-family="-apple-system, Arial, sans-serif">Build commit SHA exposed via /api/meta</text>
  </g>
'''
s3_audio = ("BloodBridge delivers six core operational capabilities. First, a donor registry that calculates dynamic ninety-day donation eligibility. "
            "Second, donation processing that converts donations into individually tracked blood units with component-specific shelf lives. "
            "Third, inventory control featuring automated quarantine, release, and a daily Kubernetes CronJob to sweep expired stock. "
            "Fourth, a prioritized hospital request queue ordered by clinical urgency and waiting time. Fifth, our smart fulfilment engine, "
            "which pairs patients with compatible units while conserving rare blood groups. And sixth, production operational endpoints "
            "including health probes, ready checks with live database validation, and Prometheus metrics.")
slides_data.append((3, "What the Application Does", "Core Capabilities: Registry, Tracking, Fulfilment & Ops", s3_content, s3_audio))

# ==========================================
# SLIDE 4: Tech Stack
# ==========================================
s4_content = '''
  <g transform="translate(120, 220)">
    <!-- Column 1 -->
    <rect x="0" y="0" width="395" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="50" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">APPLICATION TIER</text>
    <text x="40" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Full-Stack Core</text>
    
    <rect x="40" y="130" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="60" y="165" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">React 19 + Vite</text>
    <text x="60" y="195" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Tailwind CSS · Nginx runtime</text>

    <rect x="40" y="240" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="60" y="275" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">FastAPI (Python 3.13)</text>
    <text x="60" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Async endpoints · Pydantic v2</text>

    <rect x="40" y="350" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="60" y="385" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PostgreSQL 17</text>
    <text x="60" y="415" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Alembic migrations · SQLAlchemy</text>

    <rect x="40" y="460" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="60" y="495" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">pytest &amp; ruff</text>
    <text x="60" y="525" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">40 unit tests · Strict linting</text>

    <!-- Column 2 -->
    <rect x="425" y="0" width="395" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="465" y="50" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">DELIVERY TIER</text>
    <text x="465" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">DevSecOps CI/CD</text>

    <rect x="465" y="130" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="485" y="165" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GitHub Actions</text>
    <text x="485" y="195" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Parallel CI test &amp; build matrix</text>

    <rect x="465" y="240" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="485" y="275" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Docker Multi-Stage</text>
    <text x="485" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Buildx · Non-root user 10001</text>

    <rect x="465" y="350" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="485" y="385" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GHCR Container Reg</text>
    <text x="485" y="415" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">SHA-tagged immutable artifacts</text>

    <rect x="465" y="460" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="485" y="495" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Trivy + CycloneDX</text>
    <text x="485" y="525" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">CVE scanning · SBOM generation</text>

    <!-- Column 3 -->
    <rect x="850" y="0" width="395" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="890" y="50" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PLATFORM TIER</text>
    <text x="890" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Cloud &amp; GitOps</text>

    <rect x="890" y="130" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="910" y="165" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Terraform AWS</text>
    <text x="910" y="195" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">VPC · Subnets · IAM IRSA</text>

    <rect x="890" y="240" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="910" y="275" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Amazon EKS 1.34</text>
    <text x="910" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">AL2023 Managed Node Groups</text>

    <rect x="890" y="350" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="910" y="385" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Argo CD</text>
    <text x="910" y="415" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Declarative GitOps sync</text>

    <rect x="890" y="460" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="910" y="495" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Helm 3 Charts</text>
    <text x="910" y="525" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Traefik Ingress · HPA · PDB</text>

    <!-- Column 4 -->
    <rect x="1275" y="0" width="395" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1315" y="50" fill="#F59E0B" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">OBSERVABILITY TIER</text>
    <text x="1315" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Metrics &amp; Auditing</text>

    <rect x="1315" y="130" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="1335" y="165" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Prometheus</text>
    <text x="1335" y="195" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">ServiceMonitor · 15s scrape</text>

    <rect x="1315" y="240" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="1335" y="275" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Grafana Dashboards</text>
    <text x="1335" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">16 preconfigured panels</text>

    <rect x="1315" y="350" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="1335" y="385" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Alertmanager</text>
    <text x="1335" y="415" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">5 PrometheusRule alerts</text>

    <rect x="1315" y="460" width="315" height="90" rx="12" fill="#0B1324"/>
    <text x="1335" y="495" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Dependabot</text>
    <text x="1335" y="525" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Weekly security updates</text>
  </g>
'''
s4_audio = ("Our technology stack is built across four distinct layers. In the application tier, we use React nineteen with Vite for a responsive user interface, "
            "FastAPI on Python three point thirteen for asynchronous performance, PostgreSQL seventeen managed with Alembic database migrations, and pytest with Ruff for testing. "
            "In delivery, we use multi-stage Docker builds, GitHub Actions workflows, the GitHub Container Registry, and Trivy vulnerability scans coupled with CycloneDX software "
            "bills of materials. On the platform side, we manage Amazon EKS one point thirty-four and AWS VPCs via Terraform, deploying workloads with Helm three and Argo CD "
            "through Traefik Ingress. Finally, observability is driven by Prometheus, Grafana, and automated Alertmanager rules.")
slides_data.append((4, "Production Technology Stack", "Four Integrated Layers: Application, Delivery, Platform & Observability", s4_content, s4_audio))

# ==========================================
# SLIDE 5: Runtime Architecture on EKS
# ==========================================
s5_content = '''
  <g transform="translate(120, 220)">
    <!-- Big Cluster Box -->
    <rect x="0" y="0" width="1680" height="750" rx="20" fill="#090E1A" stroke="#1E2E4A" stroke-width="2"/>
    <text x="50" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">AWS REGION: ap-south-1 · EKS CLUSTER: bloodbridge-cluster</text>

    <!-- Top Traffic Ingress -->
    <g transform="translate(100, 80)">
      <rect x="0" y="0" width="260" height="90" rx="12" fill="#162238" stroke="#3B82F6" stroke-width="1.5"/>
      <text x="130" y="40" fill="#FFFFFF" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">End Users</text>
      <text x="130" y="65" fill="#94A3B8" font-size="14" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Web Browsers &amp; Hospitals</text>

      <!-- Arrow -->
      <line x1="260" y1="45" x2="350" y2="45" stroke="#60A5FA" stroke-width="3" stroke-dasharray="6,4"/>

      <!-- AWS ALB -->
      <rect x="350" y="0" width="280" height="90" rx="12" fill="#162238" stroke="#3B82F6" stroke-width="1.5"/>
      <text x="490" y="40" fill="#FFFFFF" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">AWS ALB</text>
      <text x="490" y="65" fill="#94A3B8" font-size="14" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Public Subnets (AZ a &amp; b)</text>

      <!-- Arrow -->
      <line x1="630" y1="45" x2="720" y2="45" stroke="#60A5FA" stroke-width="3" stroke-dasharray="6,4"/>

      <!-- Traefik Ingress -->
      <rect x="720" y="0" width="280" height="90" rx="12" fill="#162238" stroke="#3B82F6" stroke-width="1.5"/>
      <text x="860" y="40" fill="#FFFFFF" font-size="20" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Traefik Ingress</text>
      <text x="860" y="65" fill="#94A3B8" font-size="14" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Path routing (/ vs /api)</text>
    </g>

    <!-- Workload Namespace -->
    <rect x="80" y="220" width="1050" height="480" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="110" y="260" fill="#10B981" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">KUBERNETES NAMESPACE: bloodbridge</text>

    <!-- Frontend Pods -->
    <rect x="120" y="290" width="400" height="150" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="140" y="330" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Frontend Deployment (x2)</text>
    <text x="140" y="365" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">React 19 + Nginx runtime</text>
    <text x="140" y="395" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Path: / · Serves Static UI</text>

    <!-- Backend Pods -->
    <rect x="560" y="290" width="530" height="150" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="580" y="330" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Backend Deployment (HPA 2 → 6)</text>
    <text x="580" y="365" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">FastAPI Python 3.13 · Scaled at 60% CPU</text>
    <text x="580" y="395" fill="#60A5FA" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Path: /api · /health · /ready · /metrics</text>

    <!-- Database StatefulSet -->
    <rect x="120" y="470" width="450" height="190" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="140" y="510" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PostgreSQL 17 StatefulSet</text>
    <text x="140" y="545" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Backed by AWS EBS gp3 encrypted storage</text>
    <text x="140" y="580" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Isolated by strict Kubernetes NetworkPolicy</text>
    <text x="140" y="620" fill="#FBBF24" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Only accessible from backend namespace</text>

    <!-- CronJob -->
    <rect x="600" y="470" width="490" height="190" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="620" y="510" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Daily Expiry CronJob</text>
    <text x="620" y="545" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Runs daily at 00:00 UTC</text>
    <text x="620" y="580" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Sweeps units past shelf-life into EXPIRED</text>
    <text x="620" y="620" fill="#F87171" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Emits Prometheus expiry metric counters</text>

    <!-- GitOps & Observability Sidebar -->
    <rect x="1170" y="220" width="450" height="480" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1200" y="260" fill="#F59E0B" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GITOPS &amp; OBSERVABILITY</text>

    <!-- Argo CD Card -->
    <rect x="1200" y="290" width="390" height="150" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="1220" y="330" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Argo CD Controller</text>
    <text x="1220" y="365" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Reconciles git push to EKS state</text>
    <text x="1220" y="400" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Self-healing drift reversal enabled</text>

    <!-- Prometheus Card -->
    <rect x="1200" y="470" width="390" height="190" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
    <text x="1220" y="510" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Prometheus + Grafana</text>
    <text x="1220" y="545" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">ServiceMonitor scrapes every 15s</text>
    <text x="1220" y="580" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Alertmanager rules for low stock</text>
    <text x="1220" y="620" fill="#60A5FA" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Live Golden Signals Dashboard</text>
  </g>
'''
s5_audio = ("Here is our runtime architecture deployed in the AWS Asia Pacific South One region. End users access the application through an "
            "AWS Application Load Balancer spread across public subnets in Availability Zones A and B. Traffic enters our cluster through Traefik Ingress. "
            "Path routing directs standard traffic to two React frontend pods, while API calls route to our FastAPI backend pods, which autoscale between "
            "two and six replicas based on CPU demand. In the private subnets, PostgreSQL runs as a StatefulSet backed by encrypted Amazon EBS gp3 storage. "
            "In parallel, Prometheus scrapes application and infrastructure metrics every fifteen seconds, and Argo CD continuously reconciles our cluster "
            "against the Git repository.")
slides_data.append((5, "Runtime Architecture on Amazon EKS", "Multi-AZ Cloud Topology, Routing, Storage & Automation", s5_content, s5_audio))

# ==========================================
# SLIDE 6: CI/CD Pipeline
# ==========================================
s6_content = '''
  <g transform="translate(120, 220)">
    <!-- 5 Horizontal Stages -->
    <!-- Stage 1 -->
    <rect x="0" y="0" width="310" height="320" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="30" y="45" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STAGE 01</text>
    <text x="30" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Test</text>
    <text x="30" y="130" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Ruff static linting</text>
    <text x="30" y="165" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• 40 pytest tests</text>
    <text x="30" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Migrations on real DB</text>
    <text x="30" y="250" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ 96% Code Coverage</text>

    <!-- Stage 2 -->
    <rect x="340" y="0" width="310" height="320" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="370" y="45" fill="#F59E0B" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STAGE 02</text>
    <text x="370" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Source Scan</text>
    <text x="370" y="130" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Trivy secret scanning</text>
    <text x="370" y="165" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Dependency CVE scan</text>
    <text x="370" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• IaC misconfigurations</text>
    <text x="370" y="250" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Zero Leaked Secrets</text>

    <!-- Stage 3 -->
    <rect x="680" y="0" width="310" height="320" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="710" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STAGE 03</text>
    <text x="710" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Build</text>
    <text x="710" y="130" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Docker Buildx engine</text>
    <text x="710" y="165" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Multi-stage slim targets</text>
    <text x="710" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Tagged with commit SHA</text>
    <text x="710" y="250" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Immutable Images</text>

    <!-- Stage 4 -->
    <rect x="1020" y="0" width="310" height="320" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1050" y="45" fill="#EC4899" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STAGE 04</text>
    <text x="1050" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Image Scan</text>
    <text x="1050" y="130" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Trivy container scan</text>
    <text x="1050" y="165" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Blocks HIGH/CRITICAL</text>
    <text x="1050" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• CycloneDX SBOM created</text>
    <text x="1050" y="250" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Gate Passed Cleanly</text>

    <!-- Stage 5 -->
    <rect x="1360" y="0" width="310" height="320" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1390" y="45" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STAGE 05</text>
    <text x="1390" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GitOps Deploy</text>
    <text x="1390" y="130" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Push to GHCR registry</text>
    <text x="1390" y="165" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Auto-bump values SHA</text>
    <text x="1390" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Argo CD detects &amp; syncs</text>
    <text x="1390" y="250" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Zero Downtime Rollout</text>

    <!-- 3 Core Deployment Rules -->
    <g transform="translate(0, 370)">
      <rect x="0" y="0" width="530" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
      <circle cx="50" cy="50" r="18" fill="#EF4444" fill-opacity="0.2"/>
      <text x="50" y="57" fill="#EF4444" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">1</text>
      <text x="85" y="55" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Gate Before Push</text>
      <text x="50" y="110" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">No container artifact ever reaches the</text>
      <text x="50" y="145" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">GHCR registry unless all unit tests,</text>
      <text x="50" y="180" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">static analysis, and Trivy CVE scans</text>
      <text x="50" y="215" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">pass with zero High/Critical flaws.</text>

      <rect x="575" y="0" width="530" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
      <circle cx="625" cy="50" r="18" fill="#3B82F6" fill-opacity="0.2"/>
      <text x="625" y="57" fill="#3B82F6" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">2</text>
      <text x="660" y="55" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">SHA, Never Latest</text>
      <text x="625" y="110" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">The pipeline prohibits 'latest' tags.</text>
      <text x="625" y="145" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">Every commit produces an immutable SHA.</text>
      <text x="625" y="180" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">The running image in Kubernetes is</text>
      <text x="625" y="215" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">always traceable to its git source code.</text>

      <rect x="1150" y="0" width="530" height="350" rx="16" fill="#0B1324" stroke="#253552" stroke-width="1.5"/>
      <circle cx="1200" cy="50" r="18" fill="#10B981" fill-opacity="0.2"/>
      <text x="1200" y="57" fill="#10B981" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">3</text>
      <text x="1235" y="55" fill="#FFFFFF" font-size="22" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Pull, Not Push</text>
      <text x="1200" y="110" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">GitHub Actions CI never holds</text>
      <text x="1200" y="145" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">Kubernetes cluster credentials or IAM</text>
      <text x="1200" y="180" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">keys. Argo CD pulls declarations</text>
      <text x="1200" y="215" fill="#94A3B8" font-size="18" font-family="-apple-system, Arial, sans-serif">from Git natively inside the cluster.</text>
    </g>
  </g>
'''
s6_audio = ("Our DevSecOps pipeline executes on every push to the main branch across five sequential stages. "
            "First, tests run with Ruff linting, forty pytest tests, and schema migrations against real PostgreSQL. "
            "Second, Trivy conducts a source scan for secrets, dependency vulnerabilities, and infrastructure-as-code misconfigurations. "
            "Third, Docker Buildx compiles multi-stage container images tagged with the exact git commit SHA. "
            "Fourth, an image scan blocks any image containing High or Critical vulnerabilities and publishes a CycloneDX SBOM. "
            "Fifth, our GitOps workflow commits the updated image SHA to our Helm values repository, prompting Argo CD to deploy. "
            "We follow three golden rules: strict gates before push, commit SHA tags instead of latest, and a pull-based GitOps model where CI never holds cluster credentials.")
slides_data.append((6, "CI/CD Pipeline: Every Push to Main", "Automated Gates: Test, Scan, Build, Verify & GitOps Deploy", s6_content, s6_audio))

# ==========================================
# SLIDE 7: Pipeline Run on GitHub Actions
# ==========================================
s7_img_tag = f'<image href="data:image/png;base64,{SCREENSHOT_B64}" x="0" y="0" width="1080" height="740" preserveAspectRatio="xMidYMid meet"/>' if SCREENSHOT_B64 else '<rect width="1080" height="740" fill="#0B1324"/><text x="540" y="370" fill="#FFFFFF" text-anchor="middle" font-size="28">GitHub Actions Run #6 Screenshot</text>'

s7_content = f'''
  <g transform="translate(120, 220)">
    <!-- Screenshot Frame -->
    <rect x="0" y="0" width="1100" height="750" rx="16" fill="#000000" stroke="#1E2E4A" stroke-width="2"/>
    <g transform="translate(10, 5)">
      {s7_img_tag}
    </g>

    <!-- Right Side Metrics & Explanations -->
    <g transform="translate(1140, 0)">
      <rect x="0" y="0" width="540" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
      
      <text x="40" y="50" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">VERIFIED LIVE EXECUTION</text>
      <text x="40" y="90" fill="#FFFFFF" font-size="28" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GitHub Actions Run #6</text>
      <text x="40" y="125" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Full green execution across all supply chain stages</text>

      <rect x="40" y="155" width="460" height="110" rx="12" fill="#0B1324"/>
      <text x="60" y="195" fill="#34D399" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ 100% Green Workflow Jobs</text>
      <text x="60" y="225" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Backend CI · Frontend CI · Trivy Scan</text>
      <text x="60" y="248" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Buildx Image Push · GitOps Release Bump</text>

      <rect x="40" y="285" width="460" height="190" rx="12" fill="#0B1324"/>
      <text x="60" y="325" fill="#F59E0B" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Real-World CVE Mitigation</text>
      <text x="60" y="355" fill="#E2E8F0" font-size="14" font-family="-apple-system, Arial, sans-serif">Initial build caught 4 HIGH CVEs inside pip</text>
      <text x="60" y="380" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">(CVE-2026-97687, GHSA-6v7p-g79w-8964).</text>
      <text x="60" y="415" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Fix: Uninstalled pip from runtime image</text>
      <text x="60" y="440" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Eliminated vulnerable package without suppressions</text>

      <rect x="40" y="495" width="460" height="110" rx="12" fill="#0B1324"/>
      <text x="60" y="535" fill="#60A5FA" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">CycloneDX SBOM Artifact</text>
      <text x="60" y="565" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Automated Software Bill of Materials</text>
      <text x="60" y="588" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Exported and archived on every release run</text>

      <rect x="40" y="625" width="460" height="85" rx="12" fill="#0B1324"/>
      <text x="60" y="660" fill="#F472B6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">GitOps SHA Provenance</text>
      <text x="60" y="688" fill="#94A3B8" font-size="13" font-family="-apple-system, Arial, sans-serif">Commit tag verified in UI footer and pod metadata</text>
    </g>
  </g>
'''
s7_audio = ("This slide displays our actual GitHub Actions pipeline run number six. Every single stage executed with green checkmarks: "
            "backend unit testing, frontend build validation, Trivy container security scans, artifact generation, and GitOps release triggers. "
            "During initial development, Trivy's vulnerability gate successfully caught four High CVEs in pip dependencies vendored inside the Python runtime. "
            "Rather than suppressing these warnings, we resolved the root cause by stripping pip from the production runtime image entirely. "
            "The automated gate prevented vulnerable containers from ever entering the registry.")
slides_data.append((7, "Pipeline Run on GitHub Actions", "Green Supply Chain: Run #6, Real CVE Resolution & SBOM", s7_content, s7_audio))

# ==========================================
# SLIDE 8: Security at Every Layer
# ==========================================
s8_content = '''
  <g transform="translate(120, 220)">
    <!-- Layer 1 -->
    <rect x="0" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="50" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 01 · APPLICATION CODE</text>
    <text x="40" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Code Level Security</text>
    <text x="40" y="135" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Ruff automated security lint rules (bandit/flake8)</text>
    <text x="40" y="170" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Strict Pydantic v2 input schema validation</text>
    <text x="40" y="205" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• SQLAlchemy ORM-parameterised queries</text>
    <text x="40" y="240" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Zero SQL injection vulnerability surface</text>
    <text x="40" y="290" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Safe By Design Codebase</text>

    <!-- Layer 2 -->
    <rect x="575" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="615" y="50" fill="#F59E0B" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 02 · DEPENDENCIES</text>
    <text x="615" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Software Supply Chain</text>
    <text x="615" y="135" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Automated Trivy dependency scanning</text>
    <text x="615" y="170" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Weekly automated Dependabot PRs</text>
    <text x="615" y="205" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• CycloneDX SBOM published on each release</text>
    <text x="615" y="240" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Pinned dependency versions in lockfiles</text>
    <text x="615" y="290" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Audited Open-Source Dependencies</text>

    <!-- Layer 3 -->
    <rect x="1150" y="0" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1190" y="50" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 03 · SECRETS</text>
    <text x="1190" y="90" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Secrets Management</text>
    <text x="1190" y="135" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Trivy automated git secret scans in CI</text>
    <text x="1190" y="170" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• PostgreSQL passwords generated out-of-band</text>
    <text x="1190" y="205" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Zero plaintext credentials committed to Git</text>
    <text x="1190" y="240" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Injected via Kubernetes Secret manifests</text>
    <text x="1190" y="290" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Zero Leaked Credentials</text>

    <!-- Layer 4 -->
    <rect x="0" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="450" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 04 · CONTAINERS</text>
    <text x="40" y="490" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Container Hardening</text>
    <text x="40" y="535" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Multi-stage Docker Buildx pipeline</text>
    <text x="40" y="570" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Non-root runtime user UID/GID 10001</text>
    <text x="40" y="605" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Build tools stripped from runtime image</text>
    <text x="40" y="640" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Gate fails build on HIGH/CRITICAL CVEs</text>
    <text x="40" y="690" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Minimal Attack Surface</text>

    <!-- Layer 5 -->
    <rect x="575" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="615" y="450" fill="#8B5CF6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 05 · RUNTIME PODS</text>
    <text x="615" y="490" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Pod Security Standards</text>
    <text x="615" y="535" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Read-only root filesystem enabled</text>
    <text x="615" y="570" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• drop: [ALL] Linux capabilities</text>
    <text x="615" y="605" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• seccompProfile: RuntimeDefault</text>
    <text x="615" y="640" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• allowPrivilegeEscalation: false</text>
    <text x="615" y="690" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Restricted Pod Security Profile</text>

    <!-- Layer 6 -->
    <rect x="1150" y="400" width="530" height="350" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="1190" y="450" fill="#EC4899" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">LAYER 06 · NETWORK &amp; CLOUD</text>
    <text x="1190" y="490" fill="#FFFFFF" font-size="24" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Network &amp; IAM Security</text>
    <text x="1190" y="535" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Kubernetes NetworkPolicies enforce isolation</text>
    <text x="1190" y="570" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• PostgreSQL ingress locked to backend pods only</text>
    <text x="1190" y="605" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• AWS IRSA least-privilege IAM roles</text>
    <text x="1190" y="640" fill="#94A3B8" font-size="17" font-family="-apple-system, Arial, sans-serif">• Private VPC subnets for all compute workloads</text>
    <text x="1190" y="690" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">✓ Zero Trust Network Perimeter</text>
  </g>
'''
s8_audio = ("Security is implemented in depth at every layer of our stack. In code, Ruff enforces strict static analysis, "
            "Pydantic guarantees data validation, and SQLAlchemy prevents SQL injection through parameterized queries. At the dependency layer, "
            "automated Trivy scans and weekly Dependabot pull requests keep packages updated. For secrets, database credentials are never committed "
            "to Git and are provisioned out-of-band as Kubernetes secrets. At the container level, images run as non-root with minimal attack surfaces. "
            "At runtime, pods use read-only root filesystems, drop all Linux capabilities, and enforce seccomp profiles under Kubernetes Pod Security "
            "Standards. Finally, NetworkPolicies isolate PostgreSQL so only authorized backend pods can communicate with it.")
slides_data.append((8, "Security at Every Layer", "Defense in Depth: Code, Dependencies, Secrets, Containers & Runtime", s8_content, s8_audio))

# ==========================================
# SLIDE 9: Infrastructure as Code (Terraform)
# ==========================================
s9_content = '''
  <g transform="translate(120, 220)">
    <!-- Left Panel: VPC Topology -->
    <rect x="0" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">NETWORK TOPOLOGY</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">VPC 10.42.0.0/16 · ap-south-1</text>

    <!-- AZ a -->
    <rect x="40" y="125" width="740" height="260" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1"/>
    <text x="70" y="160" fill="#60A5FA" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Availability Zone A (ap-south-1a)</text>
    
    <rect x="70" y="180" width="330" height="175" rx="10" fill="#162238"/>
    <text x="90" y="215" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Public Subnet: 10.42.0.0/24</text>
    <text x="90" y="245" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• Internet Gateway attached</text>
    <text x="90" y="275" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• AWS ALB endpoint ingress</text>
    <text x="90" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• Tagged for Kubernetes LB</text>

    <rect x="430" y="180" width="350" height="175" rx="10" fill="#162238"/>
    <text x="450" y="215" fill="#FBBF24" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Private Subnet: 10.42.16.0/20</text>
    <text x="450" y="245" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• EKS Managed Node Group</text>
    <text x="450" y="275" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• t3.medium Amazon Linux 2023</text>
    <text x="450" y="305" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• No direct public inbound</text>

    <!-- AZ b -->
    <rect x="40" y="415" width="740" height="260" rx="12" fill="#0B1324" stroke="#253552" stroke-width="1"/>
    <text x="70" y="450" fill="#60A5FA" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Availability Zone B (ap-south-1b)</text>

    <rect x="70" y="470" width="330" height="175" rx="10" fill="#162238"/>
    <text x="90" y="505" fill="#34D399" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Public Subnet: 10.42.1.0/24</text>
    <text x="90" y="535" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• Multi-AZ redundancy</text>
    <text x="90" y="565" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• NAT Gateway egress</text>
    <text x="90" y="595" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• Elastic IP attached</text>

    <rect x="430" y="470" width="350" height="175" rx="10" fill="#162238"/>
    <text x="450" y="505" fill="#FBBF24" font-size="15" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Private Subnet: 10.42.32.0/20</text>
    <text x="450" y="535" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• EKS Managed Node Group</text>
    <text x="450" y="565" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• t3.medium Amazon Linux 2023</text>
    <text x="450" y="595" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">• High-availability worker pool</text>

    <!-- Right Panel: Terraform Specs -->
    <rect x="860" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="900" y="45" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">IAC ARCHITECTURE &amp; GOVERNANCE</text>
    <text x="900" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">EKS 1.34 &amp; AWS Modules</text>

    <rect x="900" y="125" width="740" height="160" rx="12" fill="#0B1324"/>
    <text x="930" y="165" fill="#38BDF8" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Official Community Modules</text>
    <text x="930" y="200" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• terraform-aws-modules/vpc v5.21: Multi-AZ subnets, route tables, IGW</text>
    <text x="930" y="235" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• terraform-aws-modules/eks v20.37: EKS 1.34 control plane &amp; Access Entries</text>
    <text x="930" y="265" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Managed Node Group: 2 to 4 t3.medium instances with AL2023</text>

    <rect x="900" y="315" width="740" height="180" rx="12" fill="#0B1324"/>
    <text x="930" y="355" fill="#A855F7" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Managed Cluster Add-ons</text>
    <text x="930" y="390" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• vpc-cni: Pod networking with native Kubernetes NetworkPolicy support</text>
    <text x="930" y="425" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• aws-ebs-csi-driver: Dynamic volume provisioning for PostgreSQL state</text>
    <text x="930" y="460" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• CoreDNS &amp; kube-proxy: In-cluster service discovery &amp; proxying</text>

    <rect x="900" y="525" width="740" height="180" rx="12" fill="#0B1324"/>
    <text x="930" y="565" fill="#34D399" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Operational Safety &amp; Cost Control</text>
    <text x="930" y="600" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• State locking enabled; zero credentials hardcoded; terraform.lock committed</text>
    <text x="930" y="635" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Cost efficient footprint: ~$6–8/day during evaluation</text>
    <text x="930" y="670" fill="#F87171" font-size="16" font-weight="600" font-family="-apple-system, Arial, sans-serif">Clean teardown: 'terraform destroy' fully tears down cluster and VPC</text>
  </g>
'''
s9_audio = ("All cloud infrastructure is provisioned through modular Terraform code. We deploy a custom VPC with a CIDR block of "
            "10.42.0.0/16 spanning two availability zones. Two public subnets host our external load balancers, while two private subnets "
            "house our EKS managed node groups running Amazon Linux 2023 on t3.medium instances. We leverage official AWS modules for both VPC "
            "and EKS, integrating the AWS VPC CNI with native NetworkPolicy support, CoreDNS, and the AWS EBS CSI driver using IAM Roles for Service Accounts. "
            "Terraform state is cleanly tracked, variables are git-ignored, and the entire environment can be spun up or torn down cleanly with Terraform Destroy.")
slides_data.append((9, "Infrastructure as Code with Terraform", "Multi-AZ AWS VPC, Managed EKS 1.34 & Automated Add-ons", s9_content, s9_audio))

# ==========================================
# SLIDE 10: Kubernetes & GitOps with Argo CD
# ==========================================
s10_content = '''
  <g transform="translate(120, 220)">
    <!-- Left Panel: GitOps Flow -->
    <rect x="0" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="45" fill="#F59E0B" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">DECLARATIVE AUTOMATION</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">The GitOps Reconciliation Loop</text>

    <g transform="translate(40, 130)">
      <rect x="0" y="0" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="30" y="40" fill="#60A5FA" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STEP 1 · COMMIT SHA UPDATED</text>
      <text x="30" y="75" fill="#FFFFFF" font-size="18" font-family="-apple-system, Arial, sans-serif">CI commits new image SHA to helm/bloodbridge/values-prod.yaml</text>

      <rect x="0" y="140" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="30" y="180" fill="#FBBF24" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STEP 2 · ARGO CD DETECTS DRIFT</text>
      <text x="30" y="215" fill="#FFFFFF" font-size="18" font-family="-apple-system, Arial, sans-serif">Argo CD polls Git repository (~60s), marking cluster OutOfSync</text>

      <rect x="0" y="280" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="30" y="320" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STEP 3 · AUTOMATED ROLLING SYNC</text>
      <text x="30" y="355" fill="#FFFFFF" font-size="18" font-family="-apple-system, Arial, sans-serif">Helm chart applies update; readiness probes ensure zero downtime</text>

      <rect x="0" y="420" width="740" height="140" rx="12" fill="#0B1324" stroke="#EF4444" stroke-width="1"/>
      <text x="30" y="460" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">STEP 4 · SELF-HEALING RECOVERY</text>
      <text x="30" y="495" fill="#FFFFFF" font-size="18" font-family="-apple-system, Arial, sans-serif">Manual 'kubectl scale' or 'kubectl edit' tampering is detected</text>
      <text x="30" y="525" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Argo CD immediately resets state back to the Git source of truth</text>
    </g>

    <!-- Right Panel: Workload Specs -->
    <rect x="860" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="900" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">ENTERPRISE KUBERNETES MANIFESTS</text>
    <text x="900" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Workload Architecture &amp; HA</text>

    <g transform="translate(900, 130)">
      <rect x="0" y="0" width="740" height="85" rx="12" fill="#0B1324"/>
      <text x="25" y="35" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Deployments (Frontend &amp; Backend)</text>
      <text x="25" y="65" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Frontend x2 pods · Backend startup, readiness, and liveness probes</text>

      <rect x="0" y="105" width="740" height="85" rx="12" fill="#0B1324"/>
      <text x="25" y="140" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PostgreSQL 17 StatefulSet</text>
      <text x="25" y="170" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Persistent volume claim on encrypted gp3 EBS · Stable pod identity</text>

      <rect x="0" y="210" width="740" height="85" rx="12" fill="#0B1324"/>
      <text x="25" y="245" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Horizontal Pod Autoscaler (HPA)</text>
      <text x="25" y="275" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Backend scales from 2 to 6 pods at 60% CPU utilization threshold</text>

      <rect x="0" y="315" width="740" height="85" rx="12" fill="#0B1324"/>
      <text x="25" y="350" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PodDisruptionBudget (PDB)</text>
      <text x="25" y="380" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">minAvailable: 1 guarantees zero dropped traffic during node upgrades</text>

      <rect x="0" y="420" width="740" height="85" rx="12" fill="#0B1324"/>
      <text x="25" y="455" fill="#FFFFFF" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">In-Cluster Smoke Tests (helm test)</text>
      <text x="25" y="485" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Pod verifies /ready and /api endpoints directly from within cluster</text>
    </g>
  </g>
'''
s10_audio = ("Workload orchestration is managed declaratively through Helm and Argo CD. When our CI pipeline pushes a new commit SHA "
             "to values-prod.yaml, Argo CD detects the update within sixty seconds and performs a zero-downtime rolling deployment. "
             "Argo CD also enforces automated self-healing: if an engineer manually edits a deployment or scales replicas using kubectl, "
             "Argo CD immediately flags the drift and restores the cluster to the Git source of truth. Our Helm chart manages frontend and "
             "backend deployments, PostgreSQL StatefulSets, Horizontal Pod Autoscalers, PodDisruptionBudgets, Traefik Ingress routing, "
             "NetworkPolicies, and daily CronJobs.")
slides_data.append((10, "Kubernetes, Helm and GitOps with Argo CD", "Continuous Delivery, Self-Healing & Zero-Downtime Rollouts", s10_content, s10_audio))

# ==========================================
# SLIDE 11: Live App & Concurrency Deep Dive
# ==========================================
s11_content = '''
  <g transform="translate(120, 220)">
    <!-- Fulfilment Engine Logic -->
    <rect x="0" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="45" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">ALGORITHMIC INTELLIGENCE</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Smart Fulfilment Engine</text>

    <g transform="translate(40, 130)">
      <rect x="0" y="0" width="740" height="130" rx="12" fill="#0B1324"/>
      <text x="25" y="35" fill="#60A5FA" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">1. ABO/Rh Compatibility Matrix</text>
      <text x="25" y="65" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">AB- can accept: AB-, A-, B-, and O- units.</text>
      <text x="25" y="95" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Strict medical compatibility matrix eliminates cross-match transfusion hazards.</text>

      <rect x="0" y="160" width="740" height="130" rx="12" fill="#0B1324"/>
      <text x="25" y="195" fill="#FBBF24" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">2. Conservative O- Policy</text>
      <text x="25" y="225" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Algorithm allocates specific compatible groups (e.g. A- or B-) before O-.</text>
      <text x="25" y="255" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Universal O- stock is strictly conserved for emergency situations.</text>

      <rect x="0" y="320" width="740" height="130" rx="12" fill="#0B1324"/>
      <text x="25" y="355" fill="#34D399" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">3. First-Expiring-First-Out (FEFO)</text>
      <text x="25" y="385" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Selects candidate units ordered by expires_at ASC.</text>
      <text x="25" y="415" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Older eligible blood units are issued first, preventing shelf spoilage.</text>
    </g>

    <!-- Concurrency Engine -->
    <rect x="860" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="900" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">CONCURRENCY &amp; INTEGRITY</text>
    <text x="900" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PostgreSQL Row Locking</text>

    <g transform="translate(900, 130)">
      <rect x="0" y="0" width="740" height="230" rx="12" fill="#0B1324" stroke="#3B82F6" stroke-width="1"/>
      <text x="25" y="35" fill="#38BDF8" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">SELECT FOR UPDATE SKIP LOCKED</text>
      <text x="25" y="70" fill="#94A3B8" font-size="15" font-family="Courier, monospace">SELECT * FROM blood_units</text>
      <text x="25" y="95" fill="#94A3B8" font-size="15" font-family="Courier, monospace">WHERE status = 'AVAILABLE'</text>
      <text x="25" y="120" fill="#94A3B8" font-size="15" font-family="Courier, monospace">  AND blood_group IN ('A-', 'B-', 'AB-')</text>
      <text x="25" y="145" fill="#94A3B8" font-size="15" font-family="Courier, monospace">ORDER BY expires_at ASC</text>
      <text x="25" y="170" fill="#34D399" font-size="15" font-weight="bold" font-family="Courier, monospace">FOR UPDATE SKIP LOCKED LIMIT :qty;</text>

      <rect x="0" y="260" width="740" height="310" rx="12" fill="#0B1324"/>
      <text x="25" y="295" fill="#FFFFFF" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Why Concurrency Protection Matters</text>
      <text x="25" y="335" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Hospital trauma centers submit simultaneous orders during emergencies</text>
      <text x="25" y="375" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Standard queries allow race conditions and double-allocation of same unit</text>
      <text x="25" y="415" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• SKIP LOCKED skips rows already locked by another worker transaction</text>
      <text x="25" y="455" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• High throughput: Zero transaction deadlocks, zero double-allocation</text>
    </g>
  </g>
'''
s11_audio = ("At the core of BloodBridge is our smart fulfilment algorithm in backend allocation service. "
             "When a hospital submits a critical request, the engine calculates all medically compatible donor groups using strict ABO and Rh rules. "
             "Crucially, the algorithm follows a conservative O-negative policy: it will allocate compatible non-O-negative units first, "
             "reserving universal donor stock for acute emergencies. To eliminate race conditions during high-volume hospital requests, "
             "our query engine uses PostgreSQL SELECT FOR UPDATE SKIP LOCKED. This guarantees that multiple concurrent requests can never double-book "
             "or lock the same blood unit.")
slides_data.append((11, "Live Application & Concurrency Deep Dive", "Compatibility Matching, O- Conservation & SKIP LOCKED", s11_content, s11_audio))

# ==========================================
# SLIDE 12: Observability: Prometheus & Grafana
# ==========================================
s12_content = '''
  <g transform="translate(120, 220)">
    <!-- Metrics Left -->
    <rect x="0" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="45" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">TELEMETRY &amp; GOLDEN SIGNALS</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Prometheus Instrumentation</text>

    <g transform="translate(40, 130)">
      <rect x="0" y="0" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="25" y="35" fill="#60A5FA" font-size="17" font-weight="bold" font-family="Courier, monospace">http_requests_total</text>
      <text x="25" y="65" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Tracks incoming traffic rates and status codes (2xx, 4xx, 5xx)</text>

      <rect x="0" y="130" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="25" y="165" fill="#60A5FA" font-size="17" font-weight="bold" font-family="Courier, monospace">http_request_duration_seconds</text>
      <text x="25" y="195" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Latency histogram measuring p50, p95, and p99 response times</text>

      <rect x="0" y="260" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="25" y="295" fill="#EF4444" font-size="17" font-weight="bold" font-family="Courier, monospace">bloodbridge_inventory_available_units</text>
      <text x="25" y="325" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Gauge reporting real-time available stock segmented by blood group</text>

      <rect x="0" y="390" width="740" height="110" rx="12" fill="#0B1324"/>
      <text x="25" y="425" fill="#FBBF24" font-size="17" font-weight="bold" font-family="Courier, monospace">bloodbridge_requests_open</text>
      <text x="25" y="455" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Queue depth gauge categorized by urgency: critical, emergency, routine</text>
    </g>

    <!-- Alerts Right -->
    <rect x="860" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="900" y="45" fill="#F59E0B" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">OPERATIONAL DASHBOARD</text>
    <text x="900" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Grafana &amp; Alertmanager</text>

    <g transform="translate(900, 130)">
      <rect x="0" y="0" width="740" height="230" rx="12" fill="#0B1324" stroke="#F59E0B" stroke-width="1"/>
      <text x="25" y="35" fill="#FBBF24" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">5 Automated Alertmanager Rules</text>
      <text x="25" y="70" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">• BackendDown: Fires if probe fails for &gt; 1 minute</text>
      <text x="25" y="105" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">• HighErrorRate: 5xx responses exceed 5% of total traffic</text>
      <text x="25" y="140" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">• HighLatency: p95 duration exceeds 1.0 second</text>
      <text x="25" y="175" fill="#F87171" font-size="15" font-weight="600" font-family="-apple-system, Arial, sans-serif">• BloodBridgeLowStock: Available units &lt; 5 for scarce blood groups</text>
      <text x="25" y="205" fill="#F87171" font-size="15" font-weight="600" font-family="-apple-system, Arial, sans-serif">• CriticalRequestPending: CRITICAL order unfulfilled for &gt; 15 min</text>

      <rect x="0" y="260" width="740" height="260" rx="12" fill="#0B1324"/>
      <text x="25" y="295" fill="#FFFFFF" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">16 Preconfigured Dashboard Panels</text>
      <text x="25" y="335" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Live inventory status breakdown across all 8 blood groups</text>
      <text x="25" y="375" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Golden signals: throughput, error rates, p50/p95/p99 latency</text>
      <text x="25" y="415" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">• Horizontal Pod Autoscaler replica counts, CPU &amp; memory metrics</text>
      <text x="25" y="455" fill="#34D399" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Provisioned declaratively via Helm ConfigMaps — Zero manual setup</text>
    </g>
  </g>
'''
s12_audio = ("Full-stack observability provides real-time visibility into application health and business metrics. "
             "FastAPI exposes a dedicated Prometheus metrics endpoint scraped every fifteen seconds by a Kubernetes ServiceMonitor. "
             "We track the four golden signals: request rates, error percentages, and latency percentiles. Additionally, custom business "
             "metrics monitor real-time available units per blood group and hospital queue depths. Alertmanager is configured to trigger on "
             "backend downtime, five-xx error rates exceeding five percent, or low inventory thresholds. Our pre-configured Grafana dashboard "
             "provides sixteen live panels for instant operational insight.")
slides_data.append((12, "Observability: Prometheus and Grafana", "Golden Signals, Custom Business Metrics & Low-Stock Alerts", s12_content, s12_audio))

# ==========================================
# SLIDE 13: Troubleshooting Lab
# ==========================================
s13_content = '''
  <g transform="translate(120, 220)">
    <rect x="0" y="0" width="1680" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    
    <text x="40" y="45" fill="#EF4444" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">PRODUCTION DRILLS</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Five Failure Drills in troubleshooting/RUNBOOK.md</text>

    <!-- Table Header -->
    <g transform="translate(40, 120)">
      <rect x="0" y="0" width="1600" height="50" rx="8" fill="#0B1324"/>
      <text x="20" y="32" fill="#60A5FA" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">SCENARIO</text>
      <text x="320" y="32" fill="#60A5FA" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">ROOT CAUSE</text>
      <text x="680" y="32" fill="#60A5FA" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">DIAGNOSTIC PATH</text>
      <text x="1200" y="32" fill="#60A5FA" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">RESOLUTION &amp; FIX</text>

      <!-- Row 1 -->
      <rect x="0" y="65" width="1600" height="85" rx="8" fill="#131D30"/>
      <text x="20" y="105" fill="#F87171" font-size="16" font-weight="bold" font-family="Courier, monospace">ImagePullBackOff</text>
      <text x="20" y="130" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">01-image-pull-back-off.yaml</text>
      <text x="320" y="105" fill="#FFFFFF" font-size="15" font-family="-apple-system, Arial, sans-serif">Tag never published to GHCR</text>
      <text x="320" y="130" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Typo in manifest image SHA</text>
      <text x="680" y="105" fill="#FBBF24" font-size="15" font-family="Courier, monospace">kubectl describe pod → Events</text>
      <text x="680" y="130" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Failed to pull: manifest unknown</text>
      <text x="1200" y="105" fill="#34D399" font-size="15" font-family="-apple-system, Arial, sans-serif">Point deployment to verified commit SHA</text>
      <text x="1200" y="130" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">enforced by CI pipeline output</text>

      <!-- Row 2 -->
      <rect x="0" y="165" width="1600" height="85" rx="8" fill="#131D30"/>
      <text x="20" y="205" fill="#F87171" font-size="16" font-weight="bold" font-family="Courier, monospace">No Service Endpoints</text>
      <text x="20" y="230" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">02-service-no-endpoints.yaml</text>
      <text x="320" y="205" fill="#FFFFFF" font-size="15" font-family="-apple-system, Arial, sans-serif">Service selector typo</text>
      <text x="320" y="230" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Mismatched pod label (app vs name)</text>
      <text x="680" y="205" fill="#FBBF24" font-size="15" font-family="Courier, monospace">get endpointslices · --show-labels</text>
      <text x="680" y="230" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">EndpointSlice shows 0 endpoints attached</text>
      <text x="1200" y="205" fill="#34D399" font-size="15" font-family="-apple-system, Arial, sans-serif">Patch selector label to match template</text>
      <text x="1200" y="230" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Endpoints immediately populate</text>

      <!-- Row 3 -->
      <rect x="0" y="265" width="1600" height="85" rx="8" fill="#131D30"/>
      <text x="20" y="305" fill="#F87171" font-size="16" font-weight="bold" font-family="Courier, monospace">Running, Never Ready</text>
      <text x="20" y="330" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">03-probe-failure.yaml</text>
      <text x="320" y="305" fill="#FFFFFF" font-size="15" font-family="-apple-system, Arial, sans-serif">Readiness probe on wrong port</text>
      <text x="320" y="330" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Port 8080 probed instead of 8000</text>
      <text x="680" y="305" fill="#FBBF24" font-size="15" font-family="Courier, monospace">kubectl describe pod</text>
      <text x="680" y="330" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Probe failure events, 0 container restarts</text>
      <text x="1200" y="305" fill="#34D399" font-size="15" font-family="-apple-system, Arial, sans-serif">Correct readiness port to 8000 (/ready)</text>
      <text x="1200" y="330" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Pod passes check and enters service rotation</text>

      <!-- Row 4 -->
      <rect x="0" y="365" width="1600" height="85" rx="8" fill="#131D30"/>
      <text x="20" y="405" fill="#F87171" font-size="16" font-weight="bold" font-family="Courier, monospace">OOMKilled Pod</text>
      <text x="20" y="430" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">04-oom-killed.yaml</text>
      <text x="320" y="405" fill="#FFFFFF" font-size="15" font-family="-apple-system, Arial, sans-serif">Memory limit below working set</text>
      <text x="320" y="430" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Limit set to 64Mi during batch queries</text>
      <text x="680" y="405" fill="#FBBF24" font-size="15" font-family="Courier, monospace">describe pod → Last State</text>
      <text x="680" y="430" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Terminated: Reason OOMKilled, ExitCode 137</text>
      <text x="1200" y="405" fill="#34D399" font-size="15" font-family="-apple-system, Arial, sans-serif">Adjust resource limits to 256Mi / 512Mi</text>
      <text x="1200" y="430" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Container stabilizes under peak load</text>

      <!-- Row 5 -->
      <rect x="0" y="465" width="1600" height="85" rx="8" fill="#131D30"/>
      <text x="20" y="505" fill="#F87171" font-size="16" font-weight="bold" font-family="Courier, monospace">Wrong DB Password</text>
      <text x="20" y="530" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">05-wrong-db-credentials.yaml</text>
      <text x="320" y="505" fill="#FFFFFF" font-size="15" font-family="-apple-system, Arial, sans-serif">Bad secret injected in rollout</text>
      <text x="320" y="530" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Password mismatch on authentication</text>
      <text x="680" y="505" fill="#FBBF24" font-size="15" font-family="Courier, monospace">logs --previous &amp; /ready probe</text>
      <text x="680" y="530" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Ready probe fails: DB auth error</text>
      <text x="1200" y="505" fill="#34D399" font-size="15" font-family="-apple-system, Arial, sans-serif">Old pods continue serving; zero downtime</text>
      <text x="1200" y="530" fill="#94A3B8" font-size="14" font-family="-apple-system, Arial, sans-serif">Argo CD detects and rolls back cleanly</text>
    </g>
  </g>
'''
s13_audio = ("To prepare for production anomalies, we designed a comprehensive troubleshooting lab with five failure drills in our runbook. "
             "Scenario one simulates ImagePullBackOff from an unpushed image tag, diagnosed via pod events. "
             "Scenario two simulates a service without endpoints due to a selector label typo, diagnosed using endpoint slices. "
             "Scenario three diagnoses a misconfigured readiness probe on the wrong port, where pods remain running but never ready. "
             "Scenario four resolves OOMKilled containers by analyzing exit code 137. And scenario five handles incorrect database credentials "
             "during a rolling update, proving how Kubernetes health checks keep old pods serving traffic while new pods fail safely.")
slides_data.append((13, "Troubleshooting Lab: Five Failure Drills", "Runbook Scenarios: Diagnostic Paths, Root Causes & Fixes", s13_content, s13_audio))

# ==========================================
# SLIDE 14: Key Learnings & Production Roadmap
# ==========================================
s14_content = '''
  <g transform="translate(120, 220)">
    <!-- Learnings Left -->
    <rect x="0" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="40" y="45" fill="#10B981" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">ENGINEERING REFLECTIONS</text>
    <text x="40" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Three Core Takeaways</text>

    <g transform="translate(40, 130)">
      <rect x="0" y="0" width="740" height="175" rx="12" fill="#0B1324"/>
      <circle cx="45" cy="45" r="16" fill="#3B82F6" fill-opacity="0.2"/>
      <text x="45" y="51" fill="#60A5FA" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">1</text>
      <text x="75" y="50" fill="#FFFFFF" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Readiness ≠ Liveness</text>
      <text x="45" y="95" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Checking database connectivity only inside /ready stops a temporary</text>
      <text x="45" y="125" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">database hiccup from becoming a catastrophic container restart storm.</text>
      <text x="45" y="155" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Pods temporarily remove themselves from traffic without crashing.</text>

      <rect x="0" y="195" width="740" height="175" rx="12" fill="#0B1324"/>
      <circle cx="45" cy="240" r="16" fill="#10B981" fill-opacity="0.2"/>
      <text x="45" y="246" fill="#34D399" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">2</text>
      <text x="75" y="245" fill="#FFFFFF" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Enforce Gates Before Artifacts</text>
      <text x="45" y="290" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Tests, static analysis, and Trivy security scans must complete successfully</text>
      <text x="45" y="320" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">before any container image is pushed to the GHCR registry.</text>
      <text x="45" y="350" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Prevents vulnerable or broken artifacts from ever polluting production.</text>

      <rect x="0" y="390" width="740" height="175" rx="12" fill="#0B1324"/>
      <circle cx="45" cy="435" r="16" fill="#EC4899" fill-opacity="0.2"/>
      <text x="45" y="441" fill="#F472B6" font-size="16" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">3</text>
      <text x="75" y="440" fill="#FFFFFF" font-size="20" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Git is the Single Deployment API</text>
      <text x="45" y="485" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">Using immutable commit SHA tags paired with Argo CD makes every single</text>
      <text x="45" y="515" fill="#94A3B8" font-size="16" font-family="-apple-system, Arial, sans-serif">rollout completely auditable, traceable, and trivially reversible via git revert.</text>
      <text x="45" y="545" fill="#34D399" font-size="14" font-weight="600" font-family="-apple-system, Arial, sans-serif">Zero direct manual cluster edits; declarative state is absolute.</text>
    </g>

    <!-- Roadmap Right -->
    <rect x="860" y="0" width="820" height="750" rx="16" fill="url(#cardGrad)" stroke="#1E2E4A" stroke-width="1.5"/>
    <text x="900" y="45" fill="#3B82F6" font-size="16" font-weight="bold" font-family="-apple-system, Arial, sans-serif">FUTURE HORIZONS</text>
    <text x="900" y="85" fill="#FFFFFF" font-size="26" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Production Roadmap</text>

    <g transform="translate(900, 130)">
      <rect x="0" y="0" width="740" height="90" rx="12" fill="#0B1324"/>
      <text x="25" y="35" fill="#38BDF8" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Managed Amazon RDS Aurora PostgreSQL</text>
      <text x="25" y="65" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Migrate state from in-cluster EBS StatefulSet to automated multi-AZ Aurora</text>

      <rect x="0" y="110" width="740" height="90" rx="12" fill="#0B1324"/>
      <text x="25" y="145" fill="#A855F7" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">Automated TLS with cert-manager</text>
      <text x="25" y="175" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Let's Encrypt automated certificate lifecycle for all public Ingress endpoints</text>

      <rect x="0" y="220" width="740" height="90" rx="12" fill="#0B1324"/>
      <text x="25" y="255" fill="#34D399" font-size="18" font-weight="bold" font-family="-apple-system, Arial, sans-serif">OIDC &amp; Single Sign-On Authentication</text>
      <text x="25" y="285" fill="#94A3B8" font-size="15" font-family="-apple-system, Arial, sans-serif">Hospital authentication via Keycloak / AWS Cognito with RBAC roles</text>

      <!-- Thank You Card -->
      <rect x="0" y="340" width="740" height="230" rx="16" fill="#0A1120" stroke="#EF4444" stroke-width="2"/>
      <text x="370" y="405" fill="#FFFFFF" font-size="36" font-weight="800" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Thank You!</text>
      <text x="370" y="445" fill="#E2E8F0" font-size="22" font-weight="500" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Pranay Reddy N · DevOps Final Capstone</text>
      <text x="370" y="485" fill="#EF4444" font-size="18" font-weight="bold" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">github.com/pranay-reddy2/BloodBridge</text>
      <text x="370" y="520" fill="#94A3B8" font-size="16" text-anchor="middle" font-family="-apple-system, Arial, sans-serif">Open for Questions &amp; Feedback</text>
    </g>
  </g>
'''
s14_audio = ("In conclusion, this project yielded three invaluable engineering insights. First, readiness is not liveness: "
             "checking the database only in readiness probes prevents temporary network blips from triggering catastrophic restart storms. "
             "Second, enforce gates before artifacts: automated security and unit tests must pass before container images reach the registry. "
             "Third, Git is the single source of truth: pairing immutable commit SHA tags with Argo CD makes rollouts transparent and rollbacks effortless. "
             "Looking ahead, our production roadmap includes migrating to Amazon RDS Aurora, automated TLS certificates with cert-manager, "
             "and single sign-on authentication. Thank you for your time, and please visit our GitHub repository to explore the full source code.")
slides_data.append((14, "Key Learnings & Production Roadmap", "Engineering Reflections, Supply Chain Lessons & Thank You", s14_content, s14_audio))

print(f"Total slides defined: {len(slides_data)}")

# Process slides
clip_files = []
t0 = time.time()

for num, title, subtitle, content_svg, audio_text in slides_data:
    slide_start = time.time()
    print(f"\n[Processing Slide {num}/{TOTAL_SLIDES}] {title}...")
    
    svg_str = base_slide(num, title, subtitle, content_svg)
    svg_path = f"{OUTPUT_DIR}/slide_{num:02d}.svg"
    png_path = f"{OUTPUT_DIR}/slide_{num:02d}.png"
    aiff_path = f"{OUTPUT_DIR}/slide_{num:02d}.aiff"
    clip_path = f"{OUTPUT_DIR}/clip_{num:02d}.mp4"

    # Write SVG
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_str)

    # Render PNG with sips
    subprocess.run(["sips", "-s", "format", "png", svg_path, "--out", png_path], 
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Generate Speech Audio with say -v Rishi
    subprocess.run(["say", "-v", "Rishi", "-o", aiff_path, audio_text], check=True)

    # Encode slide into MP4 with ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "25",
        "-i", png_path,
        "-i", aiff_path,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        clip_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    clip_files.append(clip_path)
    print(f"  Slide {num} rendered in {time.time() - slide_start:.2f}s")

# Concatenate all clips
print("\n[Concatenating all clips into final video...]")
concat_list = f"{OUTPUT_DIR}/concat_list.txt"
with open(concat_list, "w") as f:
    for c in clip_files:
        f.write(f"file '{c}'\n")

concat_cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c", "copy",
    "-movflags", "+faststart",
    FINAL_VIDEO
]
subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

total_dur = time.time() - t0
print(f"\n==========================================")
print(f"SUCCESS! Final presentation video generated at:")
print(f"  {FINAL_VIDEO}")
print(f"Total processing time: {total_dur:.2f} seconds")
print(f"==========================================")

# Probe final video info
res = subprocess.run(["ffprobe", "-hide_banner", FINAL_VIDEO], capture_output=True, text=True)
print(res.stderr)
