"""
AMANDA™ Demo Mode Engine
=========================
Simulated Claude responses for demonstration without API calls.

Author: rockITdata LLC
Version: 2.0.0
"""

import time
import random
from typing import Generator, Optional
from dataclasses import dataclass

# =============================================================================
# DEMO SCENARIOS
# =============================================================================

@dataclass
class DemoScenario:
    """A pre-configured demo scenario."""
    id: str
    name: str
    description: str
    bot_id: str
    interactions: list[dict]


DEMO_SCENARIOS: list[DemoScenario] = [
    DemoScenario(
        id="win_theme_discovery",
        name="Win Theme Discovery",
        description="Develop win themes for CCN Next Gen opportunity",
        bot_id="capture",
        interactions=[
            {
                "user": "Help me develop 3 compelling win themes for CCN Next Gen.\n\nCustomer: DHA/TMA\nKey Hot Buttons:\n1. Continuity of care for beneficiaries\n2. Provider network stability\n\nOur Strengths:\n1. 15 years DHA healthcare IT experience\n2. Existing provider relationships",
                "assistant": """## Win Theme Analysis for CCN Next Gen

Based on DHA/TMA's priorities and your strengths, I recommend these three win themes:

---

### 🏆 Win Theme 1: Seamless Continuity, Zero Disruption

**Feature:** Our battle-tested transition methodology, refined across 12 DHA programs, ensures parallel operations throughout migration.

**Benefit:** Beneficiaries experience uninterrupted access to care while DHA achieves modernization goals on schedule.

**Proof Point:** On the DHA MIDS contract, we migrated 2.3M patient records with 99.97% accuracy and zero service disruption, completing 30 days ahead of schedule.

*Evaluator Impact: Directly addresses their #1 hot button—continuity of care.*

---

### 🏆 Win Theme 2: Provider Network Excellence Through Relationship

**Feature:** Our team includes 8 staff with established relationships across the TRICARE provider network, including 3 former regional liaisons.

**Benefit:** DHA gains immediate access to provider insights and accelerated network optimization without the typical 6-12 month relationship-building period.

**Proof Point:** Our Provider Relations team achieved 94% provider satisfaction scores on CCN T-West, 12 points above the contract baseline.

*Evaluator Impact: Addresses network stability concern with quantified proof.*

---

### 🏆 Win Theme 3: Predictive Intelligence for Proactive Care

**Feature:** Our AI-powered analytics platform identifies care gaps 45 days earlier than traditional methods.

**Benefit:** DHA shifts from reactive to proactive beneficiary management, improving health outcomes while reducing emergency utilization costs.

**Proof Point:** Pilot deployment at Naval Medical Center San Diego reduced ER visits by 23% for high-risk beneficiaries.

*Evaluator Impact: Differentiates from competitors stuck in legacy approaches.*

---

### Recommended Integration Strategy

| Volume | Theme 1 | Theme 2 | Theme 3 |
|--------|---------|---------|---------|
| Executive Summary | Lead | Support | Support |
| Technical | Support | Lead | Lead |
| Management | Lead | Support | - |
| Past Performance | Proof | Proof | Proof |

Would you like me to develop ghost competitor profiles to stress-test these themes?"""
            },
            {
                "user": "Yes, create ghost profiles for TriWest and Optum as likely competitors.",
                "assistant": """## Ghost Competitor Analysis: CCN Next Gen

### 👻 Ghost Profile: TriWest Healthcare Alliance

**Likely Positioning:** "Incumbent Expertise & Network Depth"

**Probable Win Themes:**
1. **Network Continuity** - "Our established provider network ensures zero disruption"
2. **Institutional Knowledge** - "10+ years operating CCN regions means we know what works"
3. **Beneficiary Familiarity** - "Beneficiaries trust the TriWest name"

**Anticipated Weaknesses:**
| Weakness | Our Counter |
|----------|-------------|
| Recent OIG findings on claims processing accuracy | Emphasize our 99.97% accuracy rate and automated QA |
| Static technology platform (legacy systems) | Highlight our AI/ML capabilities and modern architecture |
| Provider satisfaction trending down (88% → 82%) | Lead with our 94% provider satisfaction proof point |
| Resistance to change/innovation | Position our "modernization without disruption" approach |

**Ghost Pricing:** Likely to bid aggressive on price to defend incumbent position. Estimate 8-12% below historical rates.

---

### 👻 Ghost Profile: Optum/UnitedHealth

**Likely Positioning:** "Commercial Scale Meets Federal Mission"

**Probable Win Themes:**
1. **Data Analytics Leadership** - "Largest healthcare data set in the nation powers predictive insights"
2. **Financial Strength** - "Resources to invest in continuous improvement"
3. **End-to-End Integration** - "Single platform for all care coordination needs"

**Anticipated Weaknesses:**
| Weakness | Our Counter |
|----------|-------------|
| Limited federal healthcare experience (mostly commercial) | Emphasize 15 years of DHA-specific experience |
| "Big company" responsiveness concerns | Highlight our SDVOSB agility and dedicated team |
| Recent DOJ investigation into Medicare practices | Position our clean compliance record |
| History of provider payment disputes | Lead with provider relationship proof points |

**Ghost Pricing:** Will likely bid at or slightly above market—relying on brand strength rather than price competition.

---

### 🎯 Competitive Counter-Strategy

**Against TriWest (Incumbent Defense):**
- Don't attack directly—evaluators may have relationships
- Focus on "building on success" language while introducing innovation
- Emphasize transition risk mitigation to address switching concerns

**Against Optum (New Entrant):**
- Highlight federal healthcare complexity they'll underestimate
- Question whether commercial approaches translate to TRICARE
- Emphasize relationship depth vs. their resource depth

**Differentiator Priority:**
1. **AI-powered proactive care** (neither competitor has this)
2. **Transition without disruption** (TriWest can't claim, Optum can't prove)
3. **Provider relationship depth** (our unique asset)

Would you like me to draft specific ghosting language for your technical volume?"""
            },
        ]
    ),
    DemoScenario(
        id="rfp_shredding",
        name="RFP Shredding",
        description="Extract requirements from sample PWS",
        bot_id="compliance",
        interactions=[
            {
                "user": "Shred this PWS excerpt and create a requirements matrix:\n\nThe contractor shall provide healthcare IT support services for the Defense Health Agency. The contractor shall maintain a minimum of 95% system uptime. The contractor should implement continuous monitoring capabilities. Technical approach will be evaluated for innovation. Past performance may include commercial contracts if federal experience is limited.",
                "assistant": """## RFP Shred Analysis

### Requirements Matrix

| ID | Section | Requirement Text | Type | Priority | Volume | Notes |
|----|---------|-----------------|------|----------|--------|-------|
| REQ-001 | PWS | Provide healthcare IT support services for DHA | SHALL | 🔴 Critical | Technical | Core scope - must address comprehensively |
| REQ-002 | PWS | Maintain minimum 95% system uptime | SHALL | 🔴 Critical | Technical | Quantified metric - need proof points |
| REQ-003 | PWS | Implement continuous monitoring capabilities | SHOULD | 🟡 Major | Technical | Not mandatory but expected |
| REQ-004 | Eval | Technical approach evaluated for innovation | EVAL | 🔴 Critical | Technical | Discriminator opportunity |
| REQ-005 | PWS | Past performance may include commercial contracts | MAY | 🟢 Minor | Past Perf | Flexibility for teaming partners |

---

### 📊 Analysis Summary

**SHALL Statements (Mandatory):** 2
- REQ-001: Healthcare IT support services
- REQ-002: 95% uptime SLA

**SHOULD Statements (Expected):** 1
- REQ-003: Continuous monitoring

**EVALUATION Criteria:** 1
- REQ-004: Innovation in technical approach

**MAY Statements (Optional):** 1
- REQ-005: Commercial PP acceptable

---

### ⚠️ Risk Flags

| Risk | Description | Mitigation |
|------|-------------|------------|
| 🔴 **Uptime SLA** | 95% is aggressive for healthcare systems | Document our historical 99.2% uptime; include redundancy architecture |
| 🟡 **Innovation Eval** | Subjective criteria—need clear differentiators | Lead with AI/ML capabilities not in incumbent solution |
| 🟡 **Continuous Monitoring** | "Should" often treated as "shall" in evaluation | Include comprehensive monitoring approach regardless |

---

### 📝 Compliance Matrix Starter

| Requirement | Response Location | Responsible | Status |
|-------------|-------------------|-------------|--------|
| REQ-001 | Tech Vol §2.1 | Mary W. | Not Started |
| REQ-002 | Tech Vol §3.4 | John S. | Not Started |
| REQ-003 | Tech Vol §3.5 | John S. | Not Started |
| REQ-004 | Tech Vol §2.0 | Mary W. | Not Started |
| REQ-005 | PP Vol §1.0 | Sarah D. | Not Started |

---

### 🎯 Next Steps

1. **Import full PWS** for complete shred
2. **Cross-reference Section M** for evaluation weights
3. **Assign section owners** to each requirement
4. **Begin drafting** high-priority SHALL responses first

Would you like me to create Section L compliance checklist for format requirements?"""
            },
        ]
    ),
    DemoScenario(
        id="compliance_check",
        name="Compliance Review",
        description="Check draft against requirements",
        bot_id="compliance",
        interactions=[
            {
                "user": "Review this draft against Section L requirement:\n\nRequirement: The Offeror shall describe their approach to maintaining 99% system availability.\n\nDraft: Our team has extensive experience maintaining high-availability systems. We use industry best practices and modern monitoring tools to ensure systems remain operational.",
                "assistant": """## Compliance Review Results

### Overall Assessment: 🟡 NEEDS WORK

---

### 🔴 CRITICAL Issues (Must Fix)

**1. Missing Quantified Commitment**
- **Requirement:** "99% system availability"
- **Your Draft:** "high-availability" (vague)
- **Fix:** State explicitly: "rockITdata commits to maintaining 99% system availability, measured monthly against the following SLA framework..."

**2. No Proof Points**
- **Requirement:** Asks for "approach" (implies methodology)
- **Your Draft:** Generic claims without evidence
- **Fix:** Add specific example: "On the DHA MIDS contract, we achieved 99.7% availability over 36 months, exceeding the 99% requirement by 0.7%."

---

### 🟡 MAJOR Issues (Should Fix)

**3. Vague Methodology**
- **Problem:** "Industry best practices" is meaningless to evaluators
- **Fix:** Name specific practices: "Our availability approach includes N+1 redundancy, automated failover within 30 seconds, and 24/7 NOC monitoring with 15-minute response SLA."

**4. Missing Monitoring Specifics**
- **Problem:** "Modern monitoring tools" lacks credibility
- **Fix:** Name tools: "We deploy Datadog for APM, PagerDuty for incident management, and custom dashboards for real-time SLA tracking."

---

### ✅ Compliant Elements

- ✓ Addresses the topic (system availability)
- ✓ Mentions experience (needs quantification)
- ✓ References monitoring (needs specifics)

---

### 📝 Recommended Rewrite

> **System Availability Approach**
>
> rockITdata commits to maintaining **99% system availability**, measured monthly in accordance with [CONTRACT] SLA requirements. Our proven availability methodology includes:
>
> **Redundancy Architecture:** All critical components deployed in N+1 configuration with automated failover completing within 30 seconds.
>
> **Proactive Monitoring:** 24/7 Network Operations Center using Datadog APM and custom health dashboards, with 15-minute response SLA for P1 incidents.
>
> **Proof of Performance:** On the DHA MIDS contract (2021-2024), rockITdata achieved **99.7% availability** over 36 months, exceeding the contractual 99% requirement while supporting 2.3M beneficiaries.

---

### Compliance Checklist

| Item | Status | Notes |
|------|--------|-------|
| Addresses requirement explicitly | 🔴 Missing | Add "99%" commitment |
| Provides methodology | 🟡 Weak | Add specific practices |
| Includes proof points | 🔴 Missing | Add past performance data |
| Uses active voice | ✅ Good | - |
| Quantifies claims | 🔴 Missing | Add metrics throughout |

Would you like me to review additional sections?"""
            },
        ]
    ),
]


# =============================================================================
# CANNED RESPONSES BY BOT TYPE
# =============================================================================

CANNED_RESPONSES = {
    "capture": {
        "default": """## Capture Strategy Analysis

I've analyzed your request from a capture strategy perspective. Here are my recommendations:

### Strategic Assessment
Based on the information provided, this opportunity aligns well with rockITdata's core capabilities in federal healthcare IT.

### Key Recommendations
1. **Develop customer-focused win themes** that address their stated priorities
2. **Map differentiators** to evaluation criteria for maximum scoring impact
3. **Identify teaming partners** to fill capability gaps early

### Risk Factors
- Incumbent advantage if recompete
- Pricing pressure in competitive environment
- Timeline constraints for team assembly

### Next Steps
1. Schedule customer discovery meeting
2. Complete competitive landscape analysis
3. Begin teaming partner outreach

Would you like me to dive deeper into any of these areas?""",
        
        "pwin": """## pWin Assessment

Based on the factors you've provided, here's my assessment:

### Current pWin Estimate: **65%**

| Factor | Score | Weight | Weighted |
|--------|-------|--------|----------|
| Customer Relationship | 4/5 | 25% | 20% |
| Solution Fit | 4/5 | 30% | 24% |
| Price Position | 3/5 | 25% | 15% |
| Past Performance | 3/5 | 20% | 12% |

### Improvement Opportunities

**Quick Wins (+5-10% pWin):**
- Schedule executive-level customer meeting
- Obtain customer reference letter

**Medium-term (+10-15% pWin):**
- Strengthen teaming arrangement
- Develop unique technical discriminator

**Investment Required (+15-20% pWin):**
- Capture manager dedicated full-time
- Competitive price-to-win analysis

Would you like me to develop an action plan for any of these?""",
    },
    
    "drafting": {
        "default": """## Draft Content

I've created the following content based on your requirements:

---

**[Section Title]**

rockITdata brings a proven approach to this requirement, developed through 15 years of federal healthcare IT delivery. Our methodology combines industry best practices with innovations developed specifically for the [AGENCY] environment.

**Our Approach:**

*Phase 1: Discovery & Planning*
We begin with comprehensive stakeholder engagement to understand current state, pain points, and success criteria. This foundation ensures our solution addresses actual needs rather than assumed requirements.

*Phase 2: Solution Design*
Our technical team develops a tailored approach that leverages existing investments while introducing targeted improvements. We prioritize solutions that minimize disruption while maximizing capability gains.

*Phase 3: Implementation & Transition*
rockITdata's battle-tested transition methodology ensures continuity of operations throughout deployment. Our parallel operations approach eliminates the "big bang" risk that plagues traditional implementations.

**Proof of Success:**
On [SIMILAR CONTRACT], rockITdata delivered [SPECIFIC OUTCOME] while [ADDITIONAL ACHIEVEMENT], demonstrating our ability to execute complex federal healthcare programs.

---

*Would you like me to strengthen any particular section or add additional proof points?*""",
    },
    
    "compliance": {
        "default": """## Compliance Analysis

I've reviewed your content against the requirements. Here's my assessment:

### Overall Compliance: 🟡 Needs Attention

---

### Findings Summary

| Severity | Count | Action Required |
|----------|-------|-----------------|
| 🔴 Critical | 1 | Must fix before submission |
| 🟡 Major | 2 | Should fix for competitive score |
| 🟢 Minor | 1 | Nice to have improvements |

### Critical Issues

**1. Missing Explicit Requirement Response**
- Requirement asks for specific methodology
- Current draft uses general language
- **Fix:** Add step-by-step process description

### Major Issues

**2. Unsupported Claim**
- Draft states "extensive experience" without evidence
- **Fix:** Add specific contract reference and metrics

**3. Format Non-Compliance**
- Exceeds recommended length for this section
- **Fix:** Tighten language, remove redundancy

### Minor Issues

**4. Passive Voice Usage**
- Several sentences use passive construction
- **Fix:** Convert to active voice for stronger impact

---

Would you like me to suggest specific rewrites for any of these issues?""",
    },
    
    "general": {
        "default": """I'd be happy to help with that! 

Based on your question, here's what I can tell you:

**Summary:**
This is a common scenario in federal proposal development. The key considerations are:

1. **Compliance First** - Ensure your response addresses all mandatory requirements
2. **Differentiation** - Look for opportunities to stand out from competitors  
3. **Evidence** - Support all claims with specific proof points

**Recommendation:**
I'd suggest starting with a clear outline that maps directly to the evaluation criteria. This ensures evaluators can easily find and score your key points.

**Next Steps:**
1. Review the Section M evaluation factors
2. Create a response outline
3. Assign subject matter experts to each section

Is there a specific aspect you'd like me to dive deeper into? I can also point you to a specialized assistant if you need:
- **Capture Assistant** for strategy questions
- **Compliance Checker** for requirement validation
- **Proposal Writer** for drafting help""",
    },
}


# =============================================================================
# DEMO ENGINE
# =============================================================================

class DemoEngine:
    """Engine for running demo scenarios with simulated responses."""
    
    def __init__(self):
        self.active_scenario: Optional[DemoScenario] = None
        self.interaction_index: int = 0
        self.demo_mode_enabled: bool = False
    
    def enable_demo_mode(self) -> None:
        """Enable demo mode."""
        self.demo_mode_enabled = True
    
    def disable_demo_mode(self) -> None:
        """Disable demo mode."""
        self.demo_mode_enabled = False
        self.active_scenario = None
        self.interaction_index = 0
    
    def is_demo_mode(self) -> bool:
        """Check if demo mode is enabled."""
        return self.demo_mode_enabled
    
    def get_scenarios(self) -> list[DemoScenario]:
        """Get all available demo scenarios."""
        return DEMO_SCENARIOS
    
    def start_scenario(self, scenario_id: str) -> Optional[dict]:
        """Start a demo scenario and return first interaction."""
        for scenario in DEMO_SCENARIOS:
            if scenario.id == scenario_id:
                self.active_scenario = scenario
                self.interaction_index = 0
                if scenario.interactions:
                    return scenario.interactions[0]
        return None
    
    def get_next_interaction(self) -> Optional[dict]:
        """Get the next interaction in the current scenario."""
        if not self.active_scenario:
            return None
        
        self.interaction_index += 1
        if self.interaction_index < len(self.active_scenario.interactions):
            return self.active_scenario.interactions[self.interaction_index]
        return None
    
    def get_demo_response(self, user_message: str, bot_id: str) -> Generator[str, None, None]:
        """
        Get a simulated response for demo mode.
        Yields characters to simulate streaming.
        """
        # Check if we're in an active scenario with matching message
        if self.active_scenario and self.interaction_index < len(self.active_scenario.interactions):
            interaction = self.active_scenario.interactions[self.interaction_index]
            if user_message.strip() == interaction["user"].strip():
                response = interaction["assistant"]
                yield from self._simulate_streaming(response)
                return
        
        # Fall back to canned responses
        bot_responses = CANNED_RESPONSES.get(bot_id, CANNED_RESPONSES["general"])
        response = bot_responses.get("default", CANNED_RESPONSES["general"]["default"])
        
        yield from self._simulate_streaming(response)
    
    def _simulate_streaming(self, text: str) -> Generator[str, None, None]:
        """Simulate streaming by yielding characters with delays."""
        words = text.split(' ')
        for i, word in enumerate(words):
            yield word
            if i < len(words) - 1:
                yield ' '
            # Small delay to simulate streaming (handled by caller)
            time.sleep(0.02)


# Global demo engine instance
demo_engine = DemoEngine()


def get_demo_engine() -> DemoEngine:
    """Get the global demo engine instance."""
    return demo_engine
