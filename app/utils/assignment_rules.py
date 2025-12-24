"""
Assignment Rules Engine
Configurable lead assignment to SDRs using Round-Robin or Territory-based rules
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.user import User
from app.models.user_company import UserCompany


class AssignmentRuleType:
    """Assignment rule types"""
    ROUND_ROBIN = "round_robin"
    TERRITORY_BASED = "territory_based"
    MANUAL = "manual"
    LOAD_BALANCED = "load_balanced"  # Assign to user with least leads


class AssignmentRulesEngine:
    """Lead assignment engine with configurable rules"""
    
    # Eligible roles for lead assignment (SDRs)
    ELIGIBLE_ROLES = ["sales_rep", "sdr", "user"]  # Can be configured
    
    @staticmethod
    def get_eligible_users(
        company_id: int,
        db: Session,
        roles: Optional[List[str]] = None
    ) -> List[User]:
        """
        Get eligible users for lead assignment
        
        Args:
            company_id: Company ID
            db: Database session
            roles: List of roles to include (default: ELIGIBLE_ROLES)
            
        Returns:
            List of eligible users
        """
        if roles is None:
            roles = AssignmentRulesEngine.ELIGIBLE_ROLES
        
        # Get users with eligible roles in the company
        eligible_users = db.query(User).join(UserCompany).filter(
            and_(
                UserCompany.company_id == company_id,
                UserCompany.role.in_(roles),
                User.is_active == True
            )
        ).all()
        
        return eligible_users
    
    @staticmethod
    def assign_round_robin(
        company_id: int,
        db: Session,
        roles: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Assign lead using round-robin algorithm
        
        Algorithm:
        1. Get all eligible users
        2. Count leads assigned to each user (recent leads, e.g., last 30 days)
        3. Assign to user with least leads
        4. If tie, assign to user who was assigned longest ago
        
        Args:
            company_id: Company ID
            db: Database session
            roles: List of roles to include
            
        Returns:
            User ID to assign, or None if no eligible users
        """
        eligible_users = AssignmentRulesEngine.get_eligible_users(company_id, db, roles)
        
        if not eligible_users:
            return None
        
        # Get lead counts for each user (active leads only)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        user_lead_counts = {}
        user_last_assignment = {}
        
        for user in eligible_users:
            # Count active leads assigned to this user
            lead_count = db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id,
                    Lead.status.notin_(["converted", "disqualified"]),
                    Lead.created_at >= thirty_days_ago
                )
            ).scalar()
            
            user_lead_counts[user.id] = lead_count or 0
            
            # Get last assignment time
            last_lead = db.query(Lead).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id
                )
            ).order_by(Lead.created_at.desc()).first()
            
            user_last_assignment[user.id] = last_lead.created_at if last_lead and last_lead.created_at else datetime.min
        
        # Find user with minimum lead count
        min_count = min(user_lead_counts.values())
        candidates = [uid for uid, count in user_lead_counts.items() if count == min_count]
        
        # If tie, pick user with oldest last assignment
        if len(candidates) > 1:
            oldest_assignment = min(user_last_assignment[uid] for uid in candidates)
            assigned_user_id = next(uid for uid in candidates if user_last_assignment[uid] == oldest_assignment)
        else:
            assigned_user_id = candidates[0]
        
        return assigned_user_id
    
    @staticmethod
    def assign_territory_based(
        company_id: int,
        country: Optional[str],
        db: Session,
        territory_map: Optional[Dict[str, int]] = None,
        roles: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Assign lead based on territory (country/region)
        
        Args:
            company_id: Company ID
            country: Lead country
            db: Database session
            territory_map: Dictionary mapping country/region to user_id
                          If None, uses default mapping or round-robin fallback
            roles: List of roles to include
            
        Returns:
            User ID to assign, or None if no eligible users
        """
        # If territory map provided and country matches, use it
        if territory_map and country:
            country_normalized = country.lower().strip()
            for territory, user_id in territory_map.items():
                if territory.lower().strip() == country_normalized:
                    # Verify user is eligible
                    user = db.query(User).join(UserCompany).filter(
                        and_(
                            User.id == user_id,
                            UserCompany.company_id == company_id,
                            User.is_active == True
                        )
                    ).first()
                    
                    if user:
                        return user_id
        
        # Fallback to round-robin if no territory match
        return AssignmentRulesEngine.assign_round_robin(company_id, db, roles)
    
    @staticmethod
    def assign_load_balanced(
        company_id: int,
        db: Session,
        roles: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Assign lead to user with least active leads (load balancing)
        
        Similar to round-robin but considers all active leads, not just recent
        
        Args:
            company_id: Company ID
            db: Database session
            roles: List of roles to include
            
        Returns:
            User ID to assign, or None if no eligible users
        """
        eligible_users = AssignmentRulesEngine.get_eligible_users(company_id, db, roles)
        
        if not eligible_users:
            return None
        
        user_lead_counts = {}
        
        for user in eligible_users:
            # Count active leads (not converted/disqualified)
            lead_count = db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id,
                    Lead.status.notin_(["converted", "disqualified"])
                )
            ).scalar()
            
            user_lead_counts[user.id] = lead_count or 0
        
        # Find user with minimum lead count
        min_count = min(user_lead_counts.values())
        assigned_user_id = next(uid for uid, count in user_lead_counts.items() if count == min_count)
        
        return assigned_user_id
    
    @staticmethod
    def assign_lead(
        company_id: int,
        rule_type: str = AssignmentRuleType.ROUND_ROBIN,
        country: Optional[str] = None,
        territory_map: Optional[Dict[str, int]] = None,
        db: Session = None,
        roles: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Assign lead based on configured rule
        
        Args:
            company_id: Company ID
            rule_type: Assignment rule type (round_robin, territory_based, load_balanced, manual)
            country: Lead country (for territory-based)
            territory_map: Territory mapping (for territory-based)
            db: Database session
            roles: List of roles to include
            
        Returns:
            User ID to assign, or None if no assignment possible
        """
        if rule_type == AssignmentRuleType.MANUAL:
            return None  # Manual assignment, don't auto-assign
        
        if rule_type == AssignmentRuleType.TERRITORY_BASED:
            return AssignmentRulesEngine.assign_territory_based(
                company_id, country, db, territory_map, roles
            )
        
        if rule_type == AssignmentRuleType.LOAD_BALANCED:
            return AssignmentRulesEngine.assign_load_balanced(company_id, db, roles)
        
        # Default: Round-robin
        return AssignmentRulesEngine.assign_round_robin(company_id, db, roles)
    
    @staticmethod
    def get_assignment_stats(
        company_id: int,
        db: Session,
        roles: Optional[List[str]] = None
    ) -> Dict:
        """
        Get assignment statistics for company
        
        Args:
            company_id: Company ID
            db: Database session
            roles: List of roles to include
            
        Returns:
            Dictionary with assignment statistics
        """
        eligible_users = AssignmentRulesEngine.get_eligible_users(company_id, db, roles)
        
        stats = {
            "total_eligible_users": len(eligible_users),
            "user_stats": []
        }
        
        for user in eligible_users:
            # Count active leads
            active_leads = db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id,
                    Lead.status.notin_(["converted", "disqualified"])
                )
            ).scalar() or 0
            
            # Count total leads (all time)
            total_leads = db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id
                )
            ).scalar() or 0
            
            # Count recent leads (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            recent_leads = db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.company_id == company_id,
                    Lead.assigned_to == user.id,
                    Lead.created_at >= thirty_days_ago
                )
            ).scalar() or 0
            
            stats["user_stats"].append({
                "user_id": user.id,
                "user_name": user.full_name,
                "user_email": user.email,
                "active_leads": active_leads,
                "total_leads": total_leads,
                "recent_leads": recent_leads
            })
        
        return stats
    
    @staticmethod
    def reassign_leads(
        company_id: int,
        rule_type: str = AssignmentRuleType.ROUND_ROBIN,
        territory_map: Optional[Dict[str, int]] = None,
        db: Session = None,
        roles: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Reassign unassigned leads based on rule
        
        Args:
            company_id: Company ID
            rule_type: Assignment rule type
            territory_map: Territory mapping (for territory-based)
            db: Database session
            roles: List of roles to include
            dry_run: If True, don't actually reassign, just return plan
            
        Returns:
            Dictionary with reassignment results
        """
        # Get unassigned leads
        unassigned_leads = db.query(Lead).filter(
            and_(
                Lead.company_id == company_id,
                Lead.assigned_to.is_(None),
                Lead.status.notin_(["converted", "disqualified"])
            )
        ).all()
        
        reassignment_plan = []
        reassigned_count = 0
        
        for lead in unassigned_leads:
            assigned_user_id = AssignmentRulesEngine.assign_lead(
                company_id=company_id,
                rule_type=rule_type,
                country=lead.country,
                territory_map=territory_map,
                db=db,
                roles=roles
            )
            
            if assigned_user_id:
                reassignment_plan.append({
                    "lead_id": lead.id,
                    "lead_name": lead.full_name,
                    "assigned_to": assigned_user_id
                })
                
                if not dry_run:
                    lead.assigned_to = assigned_user_id
                    lead.lead_owner_id = assigned_user_id
                    reassigned_count += 1
        
        if not dry_run:
            db.commit()
        
        return {
            "unassigned_leads_found": len(unassigned_leads),
            "reassigned_count": reassigned_count,
            "reassignment_plan": reassignment_plan,
            "dry_run": dry_run
        }

