import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db, engine, SessionLocal, Base
from app.core.config import settings


class TestDatabase:
    """Test cases for database configuration and utilities."""
    
    def test_engine_creation(self):
        """Test that the database engine is created with correct settings."""
        assert engine is not None
        assert str(engine.url) == settings.database_url
        
        # Test SQLite specific settings
        assert engine.pool._check_same_thread is False
    
    def test_session_local_creation(self):
        """Test that SessionLocal is properly configured."""
        assert SessionLocal is not None
        assert SessionLocal.bind == engine
        assert SessionLocal.autocommit is False
        assert SessionLocal.autoflush is False
    
    def test_base_class(self):
        """Test that the Base class is properly configured."""
        assert Base is not None
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')
    
    def test_get_db_dependency(self):
        """Test the get_db dependency function."""
        # Create a mock session
        mock_session = MagicMock()
        
        with patch('app.core.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Test that get_db yields a session and closes it
            db_gen = get_db()
            db = next(db_gen)
            
            assert db == mock_session
            mock_session_local.assert_called_once()
            
            # Test cleanup
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            mock_session.close.assert_called_once()
    
    def test_get_db_exception_handling(self):
        """Test that get_db properly handles exceptions."""
        mock_session = MagicMock()
        mock_session.close.side_effect = Exception("Close error")
        
        with patch('app.core.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            db_gen = get_db()
            db = next(db_gen)
            
            # Even if close raises an exception, the generator should complete
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            mock_session.close.assert_called_once()
    
    def test_database_url_configuration(self):
        """Test that database URL is properly configured."""
        assert settings.database_url == "sqlite:///./ops_mesh.db"
        
        # Test with different database URL
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.database_url = "postgresql://user:pass@localhost/db"
            
            # Re-import to test with new settings
            from importlib import reload
            import app.core.database
            reload(app.core.database)
    
    def test_sqlite_connection_args(self):
        """Test that SQLite connection arguments are set correctly."""
        # The engine should have check_same_thread=False for SQLite
        connect_args = engine.pool._check_same_thread
        assert connect_args is False
    
    def test_session_isolation(self):
        """Test that database sessions are properly isolated."""
        session1 = SessionLocal()
        session2 = SessionLocal()
        
        assert session1 != session2
        assert session1.bind == session2.bind
        
        session1.close()
        session2.close()
    
    def test_metadata_creation(self):
        """Test that database metadata can be created."""
        # This should not raise an exception
        Base.metadata.create_all(bind=engine)
        
        # Verify tables exist
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        
        # Should have at least the tables defined in models
        expected_tables = ['patients', 'appointments', 'queue_entries']
        for table in expected_tables:
            assert table in tables
