import smtplib
import json
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os
from twilio.rest import Client
import threading
import time

class NotificationSystem:
    def __init__(self, config_file="notification_config.json"):
        """
        Initialize the notification system for weapon detection alerts
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Notification queue
        self.notification_queue = []
        self.notification_thread = None
        self.running = False
        
        self.logger.info("Notification system initialized")
    
    def load_config(self):
        """Load notification configuration from file"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            "sms": {
                "enabled": False,
                "twilio_account_sid": "",
                "twilio_auth_token": "",
                "twilio_phone_number": "",
                "recipients": []
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "headers": {}
            },
            "alert_cooldown": 300  # 5 minutes between alerts
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
    
    def start_notification_service(self):
        """Start the notification service"""
        if self.running:
            return
        
        self.running = True
        self.notification_thread = threading.Thread(target=self._process_notifications)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        self.logger.info("Notification service started")
    
    def stop_notification_service(self):
        """Stop the notification service"""
        self.running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=5)
        self.logger.info("Notification service stopped")
    
    def _process_notifications(self):
        """Process notification queue"""
        while self.running:
            if self.notification_queue:
                notification = self.notification_queue.pop(0)
                self._send_notification(notification)
            time.sleep(1)
    
    def send_weapon_alert(self, detection, camera_info, image_path=None):
        """
        Send weapon detection alert
        
        Args:
            detection (dict): Detection information
            camera_info (dict): Camera information
            image_path (str): Path to alert image
        """
        notification = {
            'type': 'weapon_detected',
            'detection': detection,
            'camera_info': camera_info,
            'image_path': image_path,
            'timestamp': datetime.now().isoformat()
        }
        
        self.notification_queue.append(notification)
        self.logger.info(f"Queued weapon alert notification")
    
    def _send_notification(self, notification):
        """Send notification through all enabled channels"""
        try:
            # Email notification
            if self.config['email']['enabled']:
                self._send_email_notification(notification)
            
            # SMS notification
            if self.config['sms']['enabled']:
                self._send_sms_notification(notification)
            
            # Webhook notification
            if self.config['webhook']['enabled']:
                self._send_webhook_notification(notification)
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
    
    def _send_email_notification(self, notification):
        """Send email notification"""
        try:
            email_config = self.config['email']
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"WEAPON DETECTED - {notification['camera_info']['name']}"
            
            # Create email body
            body = f"""
            SECURITY ALERT - WEAPON DETECTED
            
            Camera: {notification['camera_info']['name']}
            Location: {notification['camera_info'].get('location', 'Unknown')}
            Time: {notification['timestamp']}
            
            Detection Details:
            - Weapon Type: {notification['detection']['class'].upper()}
            - Confidence: {notification['detection']['confidence']:.2%}
            - Bounding Box: {notification['detection']['bbox']}
            
            Please check the surveillance system immediately.
            
            This is an automated alert from the Weapon Detection System.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach image if available
            if notification['image_path'] and os.path.exists(notification['image_path']):
                with open(notification['image_path'], 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(notification['image_path']))
                msg.attach(image)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")
    
    def _send_sms_notification(self, notification):
        """Send SMS notification"""
        try:
            sms_config = self.config['sms']
            
            client = Client(sms_config['twilio_account_sid'], sms_config['twilio_auth_token'])
            
            message_body = f"""
            WEAPON DETECTED!
            Camera: {notification['camera_info']['name']}
            Weapon: {notification['detection']['class'].upper()}
            Confidence: {notification['detection']['confidence']:.2%}
            Time: {notification['timestamp']}
            """
            
            for recipient in sms_config['recipients']:
                message = client.messages.create(
                    body=message_body,
                    from_=sms_config['twilio_phone_number'],
                    to=recipient
                )
                self.logger.info(f"SMS sent to {recipient}: {message.sid}")
            
        except Exception as e:
            self.logger.error(f"Error sending SMS notification: {str(e)}")
    
    def _send_webhook_notification(self, notification):
        """Send webhook notification"""
        try:
            webhook_config = self.config['webhook']
            
            payload = {
                'alert_type': 'weapon_detected',
                'timestamp': notification['timestamp'],
                'camera': notification['camera_info'],
                'detection': notification['detection'],
                'image_path': notification['image_path']
            }
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config['headers'],
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Webhook notification sent successfully")
            else:
                self.logger.error(f"Webhook notification failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {str(e)}")
    
    def test_notifications(self):
        """Test all notification channels"""
        test_notification = {
            'type': 'test',
            'detection': {
                'class': 'knife',
                'confidence': 0.95,
                'bbox': [100, 100, 200, 200]
            },
            'camera_info': {
                'name': 'Test Camera',
                'location': 'Test Location'
            },
            'image_path': None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info("Testing notifications...")
        self._send_notification(test_notification)
        self.logger.info("Test notifications sent")

def create_notification_config():
    """Create a sample notification configuration file"""
    config = {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "recipients": ["security@company.com", "admin@company.com"]
        },
        "sms": {
            "enabled": True,
            "twilio_account_sid": "your-twilio-account-sid",
            "twilio_auth_token": "your-twilio-auth-token",
            "twilio_phone_number": "+1234567890",
            "recipients": ["+1234567890", "+0987654321"]
        },
        "webhook": {
            "enabled": True,
            "url": "https://your-webhook-url.com/alerts",
            "headers": {
                "Authorization": "Bearer your-token",
                "Content-Type": "application/json"
            }
        },
        "alert_cooldown": 300
    }
    
    with open("notification_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("Sample notification configuration created: notification_config.json")
    print("Please update the configuration with your actual credentials.")

if __name__ == "__main__":
    # Create sample configuration
    create_notification_config()
    
    # Test notification system
    notification_system = NotificationSystem()
    notification_system.start_notification_service()
    
    # Test notifications
    notification_system.test_notifications()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        notification_system.stop_notification_service()
        print("Notification system stopped.")
