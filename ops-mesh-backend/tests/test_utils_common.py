import pytest
from datetime import datetime
from app.models.common import generate_confirmation_code, generate_ticket_number, TimestampMixin


class TestCommonUtils:
    """Test cases for common utility functions."""
    
    def test_generate_confirmation_code_format(self):
        """Test that confirmation codes are generated in the correct format."""
        code = generate_confirmation_code()
        
        # Should be in format ABCD-1234
        assert len(code) == 9  # 4 letters + 1 dash + 4 numbers
        assert code[4] == '-'  # Dash in the middle
        
        # Split into parts
        parts = code.split('-')
        assert len(parts) == 2
        assert len(parts[0]) == 4  # Letters part
        assert len(parts[1]) == 4  # Numbers part
        
        # Check that first part contains only uppercase letters
        assert parts[0].isalpha()
        assert parts[0].isupper()
        
        # Check that second part contains only digits
        assert parts[1].isdigit()
    
    def test_generate_confirmation_code_uniqueness(self):
        """Test that confirmation codes are reasonably unique."""
        codes = set()
        
        # Generate 100 codes and check for uniqueness
        for _ in range(100):
            code = generate_confirmation_code()
            assert code not in codes, f"Duplicate code generated: {code}"
            codes.add(code)
        
        # Should have 100 unique codes
        assert len(codes) == 100
    
    def test_generate_ticket_number_format(self):
        """Test that ticket numbers are generated in the correct format."""
        ticket = generate_ticket_number()
        
        # Should be in format C-1234
        assert len(ticket) == 6  # C + 1 dash + 4 numbers
        assert ticket[1] == '-'  # Dash after C
        assert ticket.startswith('C-')
        
        # Check that the number part contains only digits
        number_part = ticket[2:]
        assert len(number_part) == 4
        assert number_part.isdigit()
    
    def test_generate_ticket_number_uniqueness(self):
        """Test that ticket numbers are reasonably unique."""
        tickets = set()
        
        # Generate 1000 tickets and check for uniqueness
        # Note: With only 4 digits, there are only 10000 possible combinations
        # So we expect some duplicates in a large sample
        for _ in range(1000):
            ticket = generate_ticket_number()
            tickets.add(ticket)
        
        # Should have high uniqueness (at least 90% unique)
        uniqueness_ratio = len(tickets) / 1000
        assert uniqueness_ratio > 0.9, f"Uniqueness ratio too low: {uniqueness_ratio:.2f}"
    
    def test_confirmation_code_randomness(self):
        """Test that confirmation codes have good randomness."""
        codes = [generate_confirmation_code() for _ in range(50)]
        
        # Check that we get variety in the letter parts
        letter_parts = [code.split('-')[0] for code in codes]
        unique_letter_parts = set(letter_parts)
        
        # Should have reasonable variety (not all the same)
        assert len(unique_letter_parts) > 1
        
        # Check that we get variety in the number parts
        number_parts = [code.split('-')[1] for code in codes]
        unique_number_parts = set(number_parts)
        
        # Should have reasonable variety (not all the same)
        assert len(unique_number_parts) > 1
    
    def test_ticket_number_randomness(self):
        """Test that ticket numbers have good randomness."""
        tickets = [generate_ticket_number() for _ in range(50)]
        
        # Check that we get variety in the number parts
        number_parts = [ticket.split('-')[1] for ticket in tickets]
        unique_number_parts = set(number_parts)
        
        # Should have reasonable variety (not all the same)
        assert len(unique_number_parts) > 1
    
    def test_timestamp_mixin_attributes(self):
        """Test that TimestampMixin has the correct attributes."""
        # Create a simple class that uses the mixin
        class TestModel(TimestampMixin):
            pass
        
        model = TestModel()
        
        # Check that attributes exist and are None by default
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert model.created_at is None
        assert model.updated_at is None
    
    def test_timestamp_mixin_type_annotations(self):
        """Test that TimestampMixin has correct type annotations."""
        # Check that the type annotations are correct
        annotations = TimestampMixin.__annotations__
        
        assert 'created_at' in annotations
        assert 'updated_at' in annotations
        
        # The annotations should indicate Optional[datetime]
        from typing import get_origin, get_args, Union
        
        created_at_type = annotations['created_at']
        updated_at_type = annotations['updated_at']
        
        # Both should be Optional types (Union[datetime, None])
        assert get_origin(created_at_type) is Union
        assert get_origin(updated_at_type) is Union
    
    def test_generate_confirmation_code_imports(self):
        """Test that generate_confirmation_code doesn't have import issues."""
        # This test ensures the function can be imported and called
        # without any import errors
        try:
            code = generate_confirmation_code()
            assert isinstance(code, str)
        except ImportError as e:
            pytest.fail(f"Import error in generate_confirmation_code: {e}")
    
    def test_generate_ticket_number_imports(self):
        """Test that generate_ticket_number doesn't have import issues."""
        # This test ensures the function can be imported and called
        # without any import errors
        try:
            ticket = generate_ticket_number()
            assert isinstance(ticket, str)
        except ImportError as e:
            pytest.fail(f"Import error in generate_ticket_number: {e}")
    
    def test_code_generation_performance(self):
        """Test that code generation is reasonably fast."""
        import time
        
        start_time = time.time()
        
        # Generate 1000 codes
        for _ in range(1000):
            generate_confirmation_code()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in less than 1 second
        assert duration < 1.0, f"Code generation took too long: {duration:.2f} seconds"
    
    def test_ticket_generation_performance(self):
        """Test that ticket generation is reasonably fast."""
        import time
        
        start_time = time.time()
        
        # Generate 1000 tickets
        for _ in range(1000):
            generate_ticket_number()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in less than 1 second
        assert duration < 1.0, f"Ticket generation took too long: {duration:.2f} seconds"
