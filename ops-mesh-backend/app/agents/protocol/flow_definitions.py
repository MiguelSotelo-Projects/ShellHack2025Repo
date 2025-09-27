"""
Patient Flow Definitions using Google ADK

This module defines the standard patient flows and templates
for the hospital operations management system.
"""

from typing import Dict, Any, List
from .agent_protocol import FlowDefinition, MessageType, MessagePriority


class PatientFlowTemplates:
    """Standard patient flow templates."""
    
    @staticmethod
    def get_appointment_checkin_flow() -> FlowDefinition:
        """Get appointment check-in flow definition."""
        return FlowDefinition(
            flow_id="appointment_checkin_v1",
            flow_name="Appointment Check-in Flow",
            version="1.0.0",
            description="Complete appointment check-in process with insurance verification and bed reservation",
            timeout_minutes=30,
            retry_policy={
                "max_retries": 3,
                "retry_delay_seconds": 5,
                "exponential_backoff": True
            },
            steps=[
                {
                    "step_id": "patient_checkin",
                    "step_name": "Patient Check-in",
                    "agent": "frontdesk",
                    "action": "patient_checkin",
                    "message_type": MessageType.PATIENT_CHECKIN,
                    "priority": MessagePriority.HIGH,
                    "timeout_minutes": 5,
                    "required": True,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_data": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "email": {"type": "string"},
                                    "medical_record_number": {"type": "string"}
                                },
                                "required": ["first_name", "last_name"]
                            },
                            "checkin_type": {
                                "type": "string",
                                "enum": ["appointment", "walkin"]
                            }
                        },
                        "required": ["patient_data", "checkin_type"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "appointment_id": {"type": "integer"},
                            "confirmation_code": {"type": "string"},
                            "status": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "appointment_verification",
                    "step_name": "Appointment Verification",
                    "agent": "scheduling",
                    "action": "verify_appointment",
                    "message_type": MessageType.APPOINTMENT_LOOKUP,
                    "priority": MessagePriority.HIGH,
                    "timeout_minutes": 3,
                    "required": True,
                    "depends_on": ["patient_checkin"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "appointment_id": {"type": "integer"},
                            "patient_id": {"type": "integer"},
                            "confirmation_code": {"type": "string"}
                        },
                        "required": ["appointment_id"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "verified": {"type": "boolean"},
                            "appointment_data": {"type": "object"},
                            "provider_available": {"type": "boolean"}
                        }
                    }
                },
                {
                    "step_id": "insurance_verification",
                    "step_name": "Insurance Verification",
                    "agent": "insurance",
                    "action": "verify_insurance",
                    "message_type": MessageType.INSURANCE_VERIFICATION,
                    "priority": MessagePriority.NORMAL,
                    "timeout_minutes": 10,
                    "required": True,
                    "depends_on": ["appointment_verification"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "appointment_id": {"type": "integer"},
                            "insurance_info": {"type": "object"}
                        },
                        "required": ["patient_id", "appointment_id"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "verified": {"type": "boolean"},
                            "coverage_info": {"type": "object"},
                            "copay_amount": {"type": "number"},
                            "patient_responsibility": {"type": "number"}
                        }
                    }
                },
                {
                    "step_id": "bed_reservation",
                    "step_name": "Bed Reservation",
                    "agent": "hospital",
                    "action": "reserve_bed",
                    "message_type": MessageType.BED_RESERVATION,
                    "priority": MessagePriority.HIGH,
                    "timeout_minutes": 5,
                    "required": True,
                    "depends_on": ["insurance_verification"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "appointment_id": {"type": "integer"},
                            "bed_type": {"type": "string"},
                            "estimated_duration": {"type": "integer"}
                        },
                        "required": ["patient_id", "appointment_id"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "reservation_id": {"type": "string"},
                            "bed_id": {"type": "string"},
                            "bed_type": {"type": "string"},
                            "location": {"type": "string"},
                            "estimated_duration": {"type": "integer"}
                        }
                    }
                },
                {
                    "step_id": "queue_placement",
                    "step_name": "Queue Placement",
                    "agent": "queue",
                    "action": "add_to_queue",
                    "message_type": MessageType.QUEUE_MANAGEMENT,
                    "priority": MessagePriority.NORMAL,
                    "timeout_minutes": 2,
                    "required": True,
                    "depends_on": ["bed_reservation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "reservation_id": {"type": "string"},
                            "bed_id": {"type": "string"},
                            "priority": {"type": "string"}
                        },
                        "required": ["patient_id", "reservation_id", "bed_id"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "queue_position": {"type": "integer"},
                            "estimated_wait_time": {"type": "integer"},
                            "ticket_number": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "staff_coordination",
                    "step_name": "Staff Coordination",
                    "agent": "staff",
                    "action": "coordinate_care",
                    "message_type": MessageType.STAFF_COORDINATION,
                    "priority": MessagePriority.NORMAL,
                    "timeout_minutes": 3,
                    "required": True,
                    "depends_on": ["queue_placement"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "bed_id": {"type": "string"},
                            "care_requirements": {"type": "object"}
                        },
                        "required": ["patient_id", "bed_id"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "assigned_staff": {"type": "array"},
                            "care_plan": {"type": "object"},
                            "estimated_start_time": {"type": "string"}
                        }
                    }
                }
            ],
            metadata={
                "category": "appointment",
                "complexity": "high",
                "estimated_duration_minutes": 30,
                "success_rate": 0.95
            }
        )
    
    @staticmethod
    def get_walkin_registration_flow() -> FlowDefinition:
        """Get walk-in registration flow definition."""
        return FlowDefinition(
            flow_id="walkin_registration_v1",
            flow_name="Walk-in Registration Flow",
            version="1.0.0",
            description="Walk-in patient registration and immediate care coordination",
            timeout_minutes=15,
            retry_policy={
                "max_retries": 2,
                "retry_delay_seconds": 3,
                "exponential_backoff": False
            },
            steps=[
                {
                    "step_id": "walkin_registration",
                    "step_name": "Walk-in Registration",
                    "agent": "frontdesk",
                    "action": "register_walkin",
                    "message_type": MessageType.WALKIN_REGISTRATION,
                    "priority": MessagePriority.HIGH,
                    "timeout_minutes": 3,
                    "required": True,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_data": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "reason": {"type": "string"}
                                },
                                "required": ["first_name", "last_name", "reason"]
                            },
                            "urgency_level": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"]
                            }
                        },
                        "required": ["patient_data", "urgency_level"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "appointment_id": {"type": "integer"},
                            "ticket_number": {"type": "string"},
                            "confirmation_code": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "emergency_bed_request",
                    "step_name": "Emergency Bed Request",
                    "agent": "hospital",
                    "action": "request_emergency_bed",
                    "message_type": MessageType.BED_RESERVATION,
                    "priority": MessagePriority.URGENT,
                    "timeout_minutes": 2,
                    "required": True,
                    "depends_on": ["walkin_registration"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "urgency_level": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["patient_id", "urgency_level"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "reservation_id": {"type": "string"},
                            "bed_id": {"type": "string"},
                            "bed_type": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "priority_queue_placement",
                    "step_name": "Priority Queue Placement",
                    "agent": "queue",
                    "action": "add_to_priority_queue",
                    "message_type": MessageType.QUEUE_MANAGEMENT,
                    "priority": MessagePriority.URGENT,
                    "timeout_minutes": 1,
                    "required": True,
                    "depends_on": ["emergency_bed_request"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "reservation_id": {"type": "string"},
                            "urgency_level": {"type": "string"},
                            "ticket_number": {"type": "string"}
                        },
                        "required": ["patient_id", "reservation_id", "urgency_level"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "queue_position": {"type": "integer"},
                            "estimated_wait_time": {"type": "integer"},
                            "priority_level": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "immediate_staff_coordination",
                    "step_name": "Immediate Staff Coordination",
                    "agent": "staff",
                    "action": "immediate_care_coordination",
                    "message_type": MessageType.STAFF_COORDINATION,
                    "priority": MessagePriority.URGENT,
                    "timeout_minutes": 2,
                    "required": True,
                    "depends_on": ["priority_queue_placement"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "bed_id": {"type": "string"},
                            "urgency_level": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["patient_id", "bed_id", "urgency_level"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "assigned_staff": {"type": "array"},
                            "immediate_actions": {"type": "array"},
                            "estimated_start_time": {"type": "string"}
                        }
                    }
                }
            ],
            metadata={
                "category": "walkin",
                "complexity": "medium",
                "estimated_duration_minutes": 15,
                "success_rate": 0.90
            }
        )
    
    @staticmethod
    def get_emergency_admission_flow() -> FlowDefinition:
        """Get emergency admission flow definition."""
        return FlowDefinition(
            flow_id="emergency_admission_v1",
            flow_name="Emergency Admission Flow",
            version="1.0.0",
            description="Emergency patient admission with immediate care coordination",
            timeout_minutes=5,
            retry_policy={
                "max_retries": 1,
                "retry_delay_seconds": 1,
                "exponential_backoff": False
            },
            steps=[
                {
                    "step_id": "emergency_checkin",
                    "step_name": "Emergency Check-in",
                    "agent": "frontdesk",
                    "action": "emergency_checkin",
                    "message_type": MessageType.PATIENT_CHECKIN,
                    "priority": MessagePriority.CRITICAL,
                    "timeout_minutes": 1,
                    "required": True,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_data": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "emergency_contact": {"type": "string"}
                                },
                                "required": ["first_name", "last_name"]
                            },
                            "emergency_type": {
                                "type": "string",
                                "enum": ["medical", "trauma", "cardiac", "stroke", "respiratory"]
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["critical", "severe", "moderate"]
                            }
                        },
                        "required": ["patient_data", "emergency_type", "severity"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "emergency_id": {"type": "string"},
                            "triage_level": {"type": "string"}
                        }
                    }
                },
                {
                    "step_id": "critical_bed_allocation",
                    "step_name": "Critical Bed Allocation",
                    "agent": "hospital",
                    "action": "allocate_critical_bed",
                    "message_type": MessageType.BED_RESERVATION,
                    "priority": MessagePriority.CRITICAL,
                    "timeout_minutes": 1,
                    "required": True,
                    "depends_on": ["emergency_checkin"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "emergency_type": {"type": "string"},
                            "severity": {"type": "string"},
                            "triage_level": {"type": "string"}
                        },
                        "required": ["patient_id", "emergency_type", "severity"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "reservation_id": {"type": "string"},
                            "bed_id": {"type": "string"},
                            "bed_type": {"type": "string"},
                            "location": {"type": "string"},
                            "equipment_required": {"type": "array"}
                        }
                    }
                },
                {
                    "step_id": "immediate_queue_bypass",
                    "step_name": "Immediate Queue Bypass",
                    "agent": "queue",
                    "action": "bypass_queue",
                    "message_type": MessageType.QUEUE_MANAGEMENT,
                    "priority": MessagePriority.CRITICAL,
                    "timeout_minutes": 1,
                    "required": True,
                    "depends_on": ["critical_bed_allocation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "reservation_id": {"type": "string"},
                            "emergency_type": {"type": "string"},
                            "severity": {"type": "string"}
                        },
                        "required": ["patient_id", "reservation_id", "emergency_type"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "immediate_care": {"type": "boolean"},
                            "estimated_start_time": {"type": "string"},
                            "priority_override": {"type": "boolean"}
                        }
                    }
                },
                {
                    "step_id": "emergency_staff_mobilization",
                    "step_name": "Emergency Staff Mobilization",
                    "agent": "staff",
                    "action": "mobilize_emergency_staff",
                    "message_type": MessageType.STAFF_COORDINATION,
                    "priority": MessagePriority.CRITICAL,
                    "timeout_minutes": 1,
                    "required": True,
                    "depends_on": ["immediate_queue_bypass"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer"},
                            "bed_id": {"type": "string"},
                            "emergency_type": {"type": "string"},
                            "severity": {"type": "string"},
                            "equipment_required": {"type": "array"}
                        },
                        "required": ["patient_id", "bed_id", "emergency_type", "severity"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "emergency_team": {"type": "array"},
                            "equipment_allocated": {"type": "array"},
                            "immediate_actions": {"type": "array"},
                            "estimated_response_time": {"type": "string"}
                        }
                    }
                }
            ],
            metadata={
                "category": "emergency",
                "complexity": "high",
                "estimated_duration_minutes": 5,
                "success_rate": 0.99
            }
        )
    
    @staticmethod
    def get_all_flows() -> Dict[str, FlowDefinition]:
        """Get all available flow definitions."""
        return {
            "appointment_checkin": PatientFlowTemplates.get_appointment_checkin_flow(),
            "walkin_registration": PatientFlowTemplates.get_walkin_registration_flow(),
            "emergency_admission": PatientFlowTemplates.get_emergency_admission_flow()
        }
    
    @staticmethod
    def get_flow_by_id(flow_id: str) -> FlowDefinition:
        """Get flow definition by ID."""
        flows = PatientFlowTemplates.get_all_flows()
        return flows.get(flow_id)
    
    @staticmethod
    def get_flows_by_category(category: str) -> Dict[str, FlowDefinition]:
        """Get flows by category."""
        all_flows = PatientFlowTemplates.get_all_flows()
        return {
            flow_id: flow_def for flow_id, flow_def in all_flows.items()
            if flow_def.metadata.get("category") == category
        }


class FlowValidator:
    """Validates flow definitions and instances."""
    
    @staticmethod
    def validate_flow_definition(flow_def: FlowDefinition) -> List[str]:
        """Validate flow definition."""
        errors = []
        
        # Check required fields
        if not flow_def.flow_id:
            errors.append("Flow ID is required")
        
        if not flow_def.flow_name:
            errors.append("Flow name is required")
        
        if not flow_def.steps:
            errors.append("Flow must have at least one step")
        
        # Validate steps
        for i, step in enumerate(flow_def.steps):
            step_errors = FlowValidator._validate_step(step, i)
            errors.extend(step_errors)
        
        # Check for circular dependencies
        dependency_errors = FlowValidator._check_circular_dependencies(flow_def.steps)
        errors.extend(dependency_errors)
        
        return errors
    
    @staticmethod
    def _validate_step(step: Dict[str, Any], step_index: int) -> List[str]:
        """Validate individual step."""
        errors = []
        
        required_fields = ["step_id", "step_name", "agent", "action", "message_type"]
        for field in required_fields:
            if field not in step:
                errors.append(f"Step {step_index}: Missing required field '{field}'")
        
        # Validate message type
        if "message_type" in step:
            try:
                MessageType(step["message_type"])
            except ValueError:
                errors.append(f"Step {step_index}: Invalid message type '{step['message_type']}'")
        
        # Validate priority
        if "priority" in step:
            try:
                MessagePriority(step["priority"])
            except ValueError:
                errors.append(f"Step {step_index}: Invalid priority '{step['priority']}'")
        
        return errors
    
    @staticmethod
    def _check_circular_dependencies(steps: List[Dict[str, Any]]) -> List[str]:
        """Check for circular dependencies in flow steps."""
        errors = []
        
        # Build dependency graph
        dependencies = {}
        for i, step in enumerate(steps):
            step_id = step.get("step_id", f"step_{i}")
            depends_on = step.get("depends_on", [])
            dependencies[step_id] = depends_on
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in dependencies:
            if step_id not in visited:
                if has_cycle(step_id):
                    errors.append(f"Circular dependency detected involving step '{step_id}'")
        
        return errors
