"""
Validation Utilities

This module provides validation functions for various data types
and business rules in the hospital management system.
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from phone_validator import PhoneNumber
import phonenumbers
from phonenumbers import NumberParseException


class ValidationError(Exception):
    """Custom validation error."""
    pass


class DataValidator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone_number(phone: str, country_code: str = "US") -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            country_code: Country code for validation
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed_number = phonenumbers.parse(phone, country_code)
            return phonenumbers.is_valid_number(parsed_number)
        except NumberParseException:
            return False
    
    @staticmethod
    def validate_date_of_birth(date_of_birth: Union[str, datetime, date]) -> bool:
        """
        Validate date of birth.
        
        Args:
            date_of_birth: Date of birth to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if isinstance(date_of_birth, str):
                dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            elif isinstance(date_of_birth, date):
                dob = datetime.combine(date_of_birth, datetime.min.time())
            else:
                dob = date_of_birth
            
            # Check if date is in the past
            if dob >= datetime.utcnow():
                return False
            
            # Check if date is not too far in the past (e.g., 150 years)
            min_date = datetime.utcnow().replace(year=datetime.utcnow().year - 150)
            if dob < min_date:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate person name.
        
        Args:
            name: Name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False
        
        # Remove extra whitespace
        name = name.strip()
        
        # Check length
        if len(name) < 1 or len(name) > 100:
            return False
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False
        
        return True
    
    @staticmethod
    def validate_appointment_time(appointment_time: Union[str, datetime]) -> bool:
        """
        Validate appointment time.
        
        Args:
            appointment_time: Appointment time to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if isinstance(appointment_time, str):
                apt_time = datetime.fromisoformat(appointment_time.replace('Z', '+00:00'))
            else:
                apt_time = appointment_time
            
            # Check if appointment is in the future
            if apt_time <= datetime.utcnow():
                return False
            
            # Check if appointment is not too far in the future (e.g., 2 years)
            max_date = datetime.utcnow().replace(year=datetime.utcnow().year + 2)
            if apt_time > max_date:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate queue priority.
        
        Args:
            priority: Priority to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_priorities = ["urgent", "high", "medium", "low"]
        return priority.lower() in valid_priorities
    
    @staticmethod
    def validate_queue_type(queue_type: str) -> bool:
        """
        Validate queue type.
        
        Args:
            queue_type: Queue type to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_types = ["appointment", "walk_in", "emergency"]
        return queue_type.lower() in valid_types
    
    @staticmethod
    def validate_appointment_type(appointment_type: str) -> bool:
        """
        Validate appointment type.
        
        Args:
            appointment_type: Appointment type to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_types = ["routine", "urgent", "follow_up", "consultation"]
        return appointment_type.lower() in valid_types
    
    @staticmethod
    def validate_patient_data(patient_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate complete patient data.
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            Dictionary with validation errors (empty if valid)
        """
        errors = {}
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "date_of_birth"]
        for field in required_fields:
            if field not in patient_data or not patient_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate first name
        if "first_name" in patient_data:
            if not DataValidator.validate_name(patient_data["first_name"]):
                errors.setdefault("first_name", []).append("Invalid first name format")
        
        # Validate last name
        if "last_name" in patient_data:
            if not DataValidator.validate_name(patient_data["last_name"]):
                errors.setdefault("last_name", []).append("Invalid last name format")
        
        # Validate date of birth
        if "date_of_birth" in patient_data:
            if not DataValidator.validate_date_of_birth(patient_data["date_of_birth"]):
                errors.setdefault("date_of_birth", []).append("Invalid date of birth")
        
        # Validate email (optional)
        if "email" in patient_data and patient_data["email"]:
            if not DataValidator.validate_email_address(patient_data["email"]):
                errors.setdefault("email", []).append("Invalid email format")
        
        # Validate phone (optional)
        if "phone" in patient_data and patient_data["phone"]:
            if not DataValidator.validate_phone_number(patient_data["phone"]):
                errors.setdefault("phone", []).append("Invalid phone number format")
        
        return errors
    
    @staticmethod
    def validate_appointment_data(appointment_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate complete appointment data.
        
        Args:
            appointment_data: Appointment data dictionary
            
        Returns:
            Dictionary with validation errors (empty if valid)
        """
        errors = {}
        
        # Validate required fields
        required_fields = ["patient_id", "appointment_date", "provider"]
        for field in required_fields:
            if field not in appointment_data or not appointment_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate patient_id
        if "patient_id" in appointment_data:
            try:
                patient_id = int(appointment_data["patient_id"])
                if patient_id <= 0:
                    errors.setdefault("patient_id", []).append("Invalid patient ID")
            except (ValueError, TypeError):
                errors.setdefault("patient_id", []).append("Patient ID must be a number")
        
        # Validate appointment date
        if "appointment_date" in appointment_data:
            if not DataValidator.validate_appointment_time(appointment_data["appointment_date"]):
                errors.setdefault("appointment_date", []).append("Invalid appointment date")
        
        # Validate appointment type (optional)
        if "appointment_type" in appointment_data and appointment_data["appointment_type"]:
            if not DataValidator.validate_appointment_type(appointment_data["appointment_type"]):
                errors.setdefault("appointment_type", []).append("Invalid appointment type")
        
        # Validate provider name
        if "provider" in appointment_data:
            if not DataValidator.validate_name(appointment_data["provider"]):
                errors.setdefault("provider", []).append("Invalid provider name")
        
        return errors
    
    @staticmethod
    def validate_walkin_data(walkin_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate walk-in registration data.
        
        Args:
            walkin_data: Walk-in data dictionary
            
        Returns:
            Dictionary with validation errors (empty if valid)
        """
        errors = {}
        
        # Validate required fields
        if "patient" not in walkin_data:
            errors.setdefault("patient", []).append("Patient data is required")
        else:
            # Validate patient data
            patient_errors = DataValidator.validate_patient_data(walkin_data["patient"])
            for field, field_errors in patient_errors.items():
                errors.setdefault(f"patient.{field}", []).extend(field_errors)
        
        # Validate priority (optional)
        if "priority" in walkin_data and walkin_data["priority"]:
            if not DataValidator.validate_priority(walkin_data["priority"]):
                errors.setdefault("priority", []).append("Invalid priority")
        
        # Validate reason (optional)
        if "reason" in walkin_data and walkin_data["reason"]:
            reason = walkin_data["reason"]
            if not isinstance(reason, str) or len(reason.strip()) == 0:
                errors.setdefault("reason", []).append("Reason must be a non-empty string")
            elif len(reason) > 500:
                errors.setdefault("reason", []).append("Reason is too long (max 500 characters)")
        
        return errors
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum length (truncate if longer)
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        # Strip whitespace
        sanitized = value.strip()
        
        # Truncate if too long
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_confirmation_code(code: str) -> bool:
        """
        Validate confirmation code format.
        
        Args:
            code: Confirmation code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not code or not isinstance(code, str):
            return False
        
        # Check format: 4 letters followed by 4 numbers (e.g., ABCD-1234)
        pattern = r"^[A-Z]{4}-[0-9]{4}$"
        return bool(re.match(pattern, code.upper()))
    
    @staticmethod
    def validate_ticket_number(ticket: str) -> bool:
        """
        Validate ticket number format.
        
        Args:
            ticket: Ticket number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not ticket or not isinstance(ticket, str):
            return False
        
        # Check format: C- followed by 4 numbers (e.g., C-1234)
        pattern = r"^C-[0-9]{4}$"
        return bool(re.match(pattern, ticket.upper()))
