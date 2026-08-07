"""
Profit Finder Tools — Government Schemes, Benefits, Profit Opportunities
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class ProfitFinder:
    """Find government schemes and profit opportunities"""

    def __init__(self):
        self.schemes = {
            'startup_india': {
                'name': 'Startup India Scheme',
                'category': 'startup',
                'benefits': 'Tax exemption, funding support, networking opportunities',
                'eligibility': 'Startups registered with DPIIT',
                'estimated_savings': 500000,
                'deadline': '2025-12-31'
            },
            'msme_subsidy': {
                'name': 'MSME Subsidy Program',
                'category': 'msme',
                'benefits': 'Financial assistance for technology upgradation',
                'eligibility': 'MSME registered enterprises',
                'estimated_savings': 250000,
                'deadline': '2025-09-30'
            },
            'export_incentive': {
                'name': 'Export Incentive Scheme',
                'category': 'export',
                'benefits': 'Duty drawback, tax rebates, subsidies',
                'eligibility': 'Registered exporters',
                'estimated_savings': 1000000,
                'deadline': '2025-06-30'
            },
            'skill_development': {
                'name': 'Skill Development Program',
                'category': 'skill',
                'benefits': 'Training subsidies, certification support',
                'eligibility': 'Companies investing in employee training',
                'estimated_savings': 150000,
                'deadline': '2025-08-15'
            },
        }

    def find_profits(self, company_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find profits based on company profile"""
        profits = []
        
        for scheme_id, scheme in self.schemes.items():
            if self._is_eligible(scheme, company_profile):
                profits.append({
                    'scheme_id': scheme_id,
                    'name': scheme['name'],
                    'category': scheme['category'],
                    'benefits': scheme['benefits'],
                    'estimated_savings': scheme['estimated_savings'],
                    'deadline': scheme['deadline'],
                    'match_reason': self._get_match_reason(scheme, company_profile)
                })
        
        return sorted(profits, key=lambda x: x['estimated_savings'], reverse=True)

    def _is_eligible(self, scheme: Dict[str, Any], company_profile: Dict[str, Any]) -> bool:
        """Check if company is eligible for scheme"""
        category = company_profile.get('category', '').lower()
        scheme_category = scheme['category'].lower()
        
        if scheme_category in ['startup', 'msme']:
            return any(kw in category for kw in [scheme_category])
        elif scheme_category == 'export':
            return company_profile.get('is_exporter', False)
        elif scheme_category == 'skill':
            return company_profile.get('has_training_program', False)
        
        return True

    def _get_match_reason(self, scheme: Dict[str, Any], company_profile: Dict[str, Any]) -> str:
        """Get reason for scheme match"""
        reasons = {
            'startup_india': 'Your company is registered as a startup',
            'msme_subsidy': 'Your company is registered as an MSME',
            'export_incentive': 'Your company is engaged in exports',
            'skill_development': 'Your company invests in employee training',
        }
        return reasons.get(scheme.get('name', ''), 'Company profile matches scheme criteria')

    def get_scheme_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed scheme information"""
        return self.schemes.get(scheme_id)

    def calculate_total_savings(self, profits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total potential savings from all matched schemes"""
        total_savings = sum(p['estimated_savings'] for p in profits)
        
        return {
            'total_savings': total_savings,
            'number_of_schemes': len(profits),
            'schemes': [{'name': p['name'], 'savings': p['estimated_savings']} for p in profits]
        }
