import io
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Dict, List

from fdk import response


class BasicAuth:
    """
    Main class implementing Basic Auth validation against multiple hardcoded users.
    Supports JSON configuration with multiple username/password pairs.
    """
    
    def __init__(self):
        self.valid_users: Dict[str, str] = {}
        self.logger = logging.getLogger()
        
    def config(self, ctx):
        """
        Reads configuration parameters and loads valid users during function initialization.
        
        Args:
            ctx: Runtime context containing configuration
        """
        self.logger.info("=== Configuration Debug Info ===")
        
        # Load multiple users from JSON configuration
        users_config = ctx.Config().get("VALID_USERS")
        if users_config and users_config.strip():
            try:
                users_array = json.loads(users_config)
                self.valid_users.clear()
                
                for user_obj in users_array:
                    username = user_obj.get("username")
                    password = user_obj.get("password")
                    if username and password:
                        self.valid_users[username] = password
                
                self.logger.info(f"Loaded {len(self.valid_users)} valid users")
            except Exception as e:
                self.logger.error(f"Error parsing VALID_USERS configuration: {str(e)}")
                self.valid_users.clear()
        
        # Log configuration status for debugging
        self.logger.info(f"VALID_USERS: {len(self.valid_users)} users loaded" if self.valid_users else "NULL")
        self.logger.info("=== End Configuration Debug ===")
    
    def is_config_valid(self) -> bool:
        """
        Returns True if configuration is valid (has users loaded), False otherwise.
        
        Returns:
            bool: True if valid users are loaded
        """
        return len(self.valid_users) > 0
    
    def get_user_details_from_token(self, token: str) -> List[str]:
        """
        Decodes Basic Auth token and extracts username and password.
        
        Args:
            token: Basic auth token (e.g., "Basic <base64-encoded-credentials>")
            
        Returns:
            List[str]: [username, password] or empty list if invalid
        """
        try:
            # Remove "Basic " prefix
            if not token.startswith("Basic "):
                return []
            
            encoded_data = token[6:]  # Remove "Basic " prefix
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            user_credentials = decoded_data.split(":", 1)  # Split only on first colon
            
            if len(user_credentials) == 2:
                return user_credentials
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error decoding token: {str(e)}")
            return []
    
    def handle_request(self, ctx, data: io.BytesIO = None):
        """
        Main entry point for the function - validates Basic Auth against multiple users.
        
        Args:
            ctx: Function context
            data: Input data containing the request
            
        Returns:
            response.Response: Authentication result
        """
        result = {
            "active": False,
            "principal": None
        }
        
        # Check if configuration is valid
        if not self.is_config_valid():
            self.logger.error("Function initialization error, VALID_USERS configuration not set")
            return response.Response(
                ctx, 
                response_data=json.dumps(result),
                headers={"Content-Type": "application/json"}
            )
        
        try:
            # Parse input data
            if data:
                input_data = json.loads(data.getvalue())
                token = input_data.get("token")
            else:
                token = None
            
            # Check for Basic auth token
            if not token or not token.startswith("Basic "):
                self.logger.error("Request error, missing or invalid Basic auth token")
                return response.Response(
                    ctx,
                    response_data=json.dumps(result),
                    headers={"Content-Type": "application/json"}
                )
            
            # Extract and decode Basic auth credentials
            user_credentials = self.get_user_details_from_token(token)
            if len(user_credentials) != 2 or not user_credentials[0] or not user_credentials[1]:
                self.logger.error("Request error username or password missing")
                return response.Response(
                    ctx,
                    response_data=json.dumps(result),
                    headers={"Content-Type": "application/json"}
                )
            
            username, password = user_credentials
            
            # Validate against multiple users
            if username in self.valid_users and self.valid_users[username] == password:
                result["active"] = True
                result["principal"] = username
                
                self.logger.info(f"Basic Auth validation successful for user: {username}")
            else:
                self.logger.error(f"Invalid username or password for user: {username}")
            
            return response.Response(
                ctx,
                response_data=json.dumps(result),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return response.Response(
                ctx,
                response_data=json.dumps(result),
                headers={"Content-Type": "application/json"}
            )


# Global instance
basic_auth_handler = BasicAuth()


def handler(ctx, data: io.BytesIO = None):
    """
    Main handler function for Oracle Functions.
    
    Args:
        ctx: Function context
        data: Input data
        
    Returns:
        response.Response: Authentication result
    """
    # Initialize configuration on first call
    if not basic_auth_handler.valid_users:
        basic_auth_handler.config(ctx)
    
    return basic_auth_handler.handle_request(ctx, data)
