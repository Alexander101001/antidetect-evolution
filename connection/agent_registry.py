"""
📋 66 AGENT REGISTRY
All agents live in the antidetect-evolution repo.
This file tracks them all.
"""
import os
import json
from pathlib import Path

# The 66 agents, organized by function
AGENTS = {
    # ===== CORE SYSTEM (10) =====
    "core": [
        ("base_agent", "Base class for all agents"),
        ("master_orchestrator", "Coordinates all agents"),
        ("github_hf_bridge", "Connects GitHub ↔ HF"),
        ("state_manager", "Persists agent state"),
        ("config_manager", "Manages configuration"),
        ("logger", "Centralized logging"),
        ("error_handler", "Graceful error recovery"),
        ("scheduler", "Cron-like scheduling"),
        ("rate_limiter", "API rate limit handling"),
        ("message_bus", "Inter-agent communication"),
    ],
    
    # ===== RESEARCH (8) =====
    "research": [
        ("ai_research_agent", "AI-powered research"),
        ("trend_detector", "Finds trending topics"),
        ("competitor_analyzer", "Analyzes competitors"),
        ("keyword_researcher", "SEO keyword research"),
        ("market_analyzer", "Market size estimation"),
        ("opportunity_finder", "Finds gaps in market"),
        ("content_researcher", "Researches content topics"),
        ("user_behavior_analyzer", "Analyzes user patterns"),
    ],
    
    # ===== CREATION (10) =====
    "creation": [
        ("tool_generator", "Creates new tools"),
        ("content_writer", "Writes blog posts"),
        ("code_writer", "Generates code"),
        ("image_generator", "AI image creation"),
        ("video_creator", "Video content"),
        ("tweet_writer", "Social media posts"),
        ("email_writer", "Email sequences"),
        ("ad_copywriter", "Ad copy"),
        ("seo_writer", "SEO content"),
        ("script_writer", "Video scripts"),
    ],
    
    # ===== OPTIMIZATION (8) =====
    "optimization": [
        ("seo_optimizer", "SEO improvement"),
        ("performance_optimizer", "Speed optimization"),
        ("conversion_optimizer", "Conversion rate improvement"),
        ("ad_optimizer", "Ad performance"),
        ("content_optimizer", "Content quality"),
        ("ui_ux_optimizer", "User experience"),
        ("a_b_tester", "A/B testing"),
        ("analytics_analyzer", "Performance analysis"),
    ],
    
    # ===== REVENUE (10) =====
    "revenue": [
        ("ad_manager", "Manages 10 ad platforms"),
        ("affiliate_manager", "Affiliate programs"),
        ("pricing_optimizer", "Price optimization"),
        ("subscription_manager", "Subscription services"),
        ("payment_processor", "Payment handling"),
        ("invoice_generator", "Invoice creation"),
        ("revenue_tracker", "Track all revenue"),
        ("tax_calculator", "Tax estimation"),
        ("payout_manager", "Manage payouts"),
        ("financial_reporter", "Financial reports"),
    ],
    
    # ===== DISTRIBUTION (8) =====
    "distribution": [
        ("social_poster", "Auto-post to social"),
        ("directory_submitter", "Submit to directories"),
        ("seo_distributor", "SEO distribution"),
        ("email_marketer", "Email campaigns"),
        ("community_manager", "Forum/community engagement"),
        ("influencer_finder", "Find influencers"),
        ("cross_poster", "Cross-platform posting"),
        ("traffic_driver", "Traffic generation"),
    ],
    
    # ===== INTELLIGENCE (6) =====
    "intelligence": [
        ("intelligence_test", "Daily IQ test"),
        ("self_improver", "Self-improvement loop"),
        ("strategy_learner", "Learn from successes"),
        ("pattern_recognizer", "Find patterns"),
        ("predictor", "Predict trends"),
        ("decision_maker", "Make optimal decisions"),
    ],
    
    # ===== UTILITIES (6) =====
    "utility": [
        ("github_agent", "GitHub operations"),
        ("hf_agent", "Hugging Face operations"),
        ("cloud_deploy", "Cloud deployment"),
        ("backup_manager", "Backup everything"),
        ("security_scanner", "Security checks"),
        ("performance_monitor", "System monitoring"),
    ],
}

def count_agents():
    total = sum(len(agents) for agents in AGENTS.values())
    return total

def list_all_agents():
    all_agents = []
    for category, agents in AGENTS.items():
        for name, desc in agents:
            all_agents.append({
                "name": name,
                "category": category,
                "description": desc,
                "path": f"agents/{name}.py"
            })
    return all_agents

if __name__ == "__main__":
    total = count_agents()
    print(f"📋 Total agents: {total}")
    print()
    
    for category, agents in AGENTS.items():
        print(f"\n{category.upper()} ({len(agents)} agents):")
        for name, desc in agents:
            print(f"   • {name} — {desc}")
