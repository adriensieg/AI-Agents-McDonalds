from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent

class WebAutomationAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("WebAutomationAgent", "Browser automation for UberEats ordering", 9003)
        self.selenium_tools = None

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="web_automation",
                name="Web Browser Automation",
                description="Automates browser interactions for food ordering",
                tags=["selenium", "browser", "automation", "ubereats"],
                examples=["navigate to restaurant", "add items to cart", "fill forms"]
            ),
            AgentSkill(
                id="site_navigation",
                name="Site Navigation",
                description="Navigates UberEats website structure",
                tags=["navigation", "search", "menu"],
                examples=["find mcdonalds", "search menu items", "locate add to cart"]
            )
        ]

        return AgentCard(
            name="Web Automation Agent",
            description="Browser automation specialist for food ordering",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["json"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=False),
            skills=skills
        )

    async def get_selenium_tools(self):
        if not self.selenium_tools:
            mcp_params = StdioServerParameters(
                command="selenium-mcp-server",
                args=["--headless", "--ubereats-mode"]
            )

            toolset = MCPToolset("selenium_automation", mcp_params)
            self.selenium_tools, _ = await toolset.get_tools_async()

        return self.selenium_tools

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Starting web automation: {message}")

        try:
            tools = await self.get_selenium_tools()

            web_agent = LlmAgent(
                model='gemini-2.0-flash',
                name='ubereats_automation',
                instruction=(
                    "You are a UberEats web automation specialist. Navigate to UberEats.com, "
                    "search for McDonald's, add specified items to cart, and prepare for checkout. "
                    "Use browser tools methodically: navigate -> search -> select items -> add to cart. "
                    "Always confirm each step before proceeding to the next."
                ),
                tools=tools
            )

            order_details = message.get("order_details", [])
            automation_prompt = f"""
            Please automate the following UberEats order:
            1. Navigate to UberEats.com
            2. Search for McDonald's restaurants in Chicago
            3. Select the McDonald's Global Menu Restaurant
            4. Add these items to cart: {', '.join(order_details)}
            5. Proceed to cart review (but don't complete checkout yet)

            Return the cart ID and status when ready for checkout.
            """

            result = await web_agent.process_message(automation_prompt)

            return {
                "status": "ready_for_checkout",
                "cart_id": "cart_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                "items_added": order_details,
                "automation_log": result
            }

        except Exception as e:
            self.logger.error(f"Web automation failed: {str(e)}")
            return {
                "status": "automation_failed",
                "error": str(e)
            }

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class McDonaldsOrderBot:
    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver with options"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-geolocation")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable location services
        prefs = {
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def navigate_to_ubereats(self):
        """Navigate to Uber Eats and handle location popup"""
        logger.info("Navigating to Uber Eats...")
        self.driver.get('https://www.ubereats.com')
        time.sleep(3)
        
        # Handle location popup immediately
        self.handle_location_popup()
        
    def handle_location_popup(self):
        """Handle the location selection popup"""
        try:
            logger.info("Handling location popup...")
            
            # Wait a moment for popup to appear
            time.sleep(2)
            
            # Common selectors for location popup elements
            popup_selectors = [
                # Close button selectors
                "button[aria-label='Close']",
                "button[data-testid='close-button']",
                ".close-button",
                "[data-testid*='close']",
                "button:contains('×')",
                "button:contains('Close')",
                
                # Deny/Block location buttons
                "button:contains('Block')",
                "button:contains('Deny')",
                "button:contains('Not now')",
                "button:contains('No thanks')",
                
                # Skip location buttons
                "button:contains('Skip')",
                "button:contains('Maybe later')",
                "a:contains('Skip')"
            ]
            
            popup_closed = False
            
            # Try to find and close the popup
            for selector in popup_selectors:
                try:
                    if "contains" in selector:
                        # Use XPath for text-based selectors
                        text_to_find = selector.split("'")[1]
                        element = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text_to_find}')] | //a[contains(text(), '{text_to_find}')]"))
                        )
                    else:
                        # Use CSS selector
                        element = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    element.click()
                    time.sleep(1)
                    logger.info(f"Successfully closed popup using: {selector}")
                    popup_closed = True
                    break
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    continue
            
            # If popup still exists, try pressing ESC key
            if not popup_closed:
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    logger.info("Tried closing popup with ESC key")
                except:
                    pass
            
            # Alternative: Try to click outside the popup to dismiss it
            if not popup_closed:
                try:
                    self.driver.execute_script("document.body.click();")
                    time.sleep(1)
                    logger.info("Tried clicking outside popup to dismiss")
                except:
                    pass
            
            # Check if there's still a modal/overlay and try to remove it
            self.remove_modal_overlays()
            
        except Exception as e:
            logger.warning(f"Could not handle location popup: {e}")
            # Continue anyway - sometimes the popup doesn't appear
            
    def remove_modal_overlays(self):
        """Remove any modal overlays that might be blocking interaction"""
        try:
            # Common overlay/modal selectors
            overlay_selectors = [
                ".modal-backdrop",
                ".overlay",
                "[data-testid*='modal']",
                "[role='dialog']",
                ".popup-overlay"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for overlay in overlays:
                        self.driver.execute_script("arguments[0].remove();", overlay)
                    if overlays:
                        logger.info(f"Removed {len(overlays)} overlay(s) with selector: {selector}")
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Error removing overlays: {e}")
        
    def set_delivery_address(self, address="110 N Carpenter Street, Chicago, IL"):
        """Set the delivery address to find the McDonald's location"""
        try:
            logger.info(f"Setting delivery address to: {address}")
            
            # Look for address input field
            address_selectors = [
                "[data-testid='address-input']",
                "input[placeholder*='address']",
                "input[placeholder*='Address']",
                "#location-typeahead-home-input",
                "[aria-label*='address']"
            ]
            
            address_input = None
            for selector in address_selectors:
                try:
                    address_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
                    
            if not address_input:
                logger.error("Could not find address input field")
                return False
                
            address_input.clear()
            address_input.send_keys(address)
            time.sleep(2)
            address_input.send_keys(Keys.ENTER)
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting delivery address: {e}")
            return False
    
    def search_mcdonalds(self):
        """Search for McDonald's restaurant"""
        try:
            logger.info("Searching for McDonald's...")
            
            # Try to find search input
            search_selectors = [
                "input[placeholder*='Search']",
                "input[data-testid='store-search-input']",
                "[aria-label*='Search']",
                "input[type='search']"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
                    
            if search_input:
                search_input.clear()
                search_input.send_keys("McDonald's")
                search_input.send_keys(Keys.ENTER)
                time.sleep(3)
            
            # Look for McDonald's restaurant link
            mcdonalds_selectors = [
                "a[href*='mcdonalds']",
                "[data-testid*='store-card'] a:contains('McDonald\\'s')",
                "a:contains('McDonald\\'s')"
            ]
            
            for selector in mcdonalds_selectors:
                try:
                    mcdonalds_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    mcdonalds_link.click()
                    time.sleep(5)
                    logger.info("Successfully clicked on McDonald's restaurant")
                    return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error searching for McDonald's: {e}")
            return False
    
    def find_global_favorites_section(self):
        """Find and navigate to Global Favorites section"""
        try:
            logger.info("Looking for Global Favorites section...")
            
            # Possible selectors for Global Favorites
            global_favorites_selectors = [
                "button:contains('Global Favorites')",
                "[data-testid*='global-favorites']",
                "a:contains('Global Favorites')",
                "[aria-label*='Global Favorites']",
                "div:contains('Global Favorites')"
            ]
            
            # Scroll down to find more menu sections
            self.driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            
            for selector in global_favorites_selectors:
                try:
                    section = self.driver.find_element(By.XPATH, f"//*[contains(text(), 'Global Favorites')]")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", section)
                    time.sleep(1)
                    if section.is_displayed():
                        section.click()
                        time.sleep(3)
                        logger.info("Found and clicked Global Favorites section")
                        return True
                except:
                    continue
                    
            # If not found, try to scroll and look for menu categories
            self.scroll_to_find_section("Global Favorites")
            return True
            
        except Exception as e:
            logger.error(f"Error finding Global Favorites section: {e}")
            return False
    
    def scroll_to_find_section(self, section_name):
        """Scroll through the page to find a specific section"""
        logger.info(f"Scrolling to find {section_name} section...")
        
        for i in range(10):  # Scroll down 10 times
            self.driver.execute_script(f"window.scrollTo(0, {500 * (i + 1)});")
            time.sleep(1)
            
            try:
                section = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{section_name}')]")
                if section.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", section)
                    time.sleep(1)
                    return True
            except:
                continue
                
        return False
    
    def add_global_favorites_items(self):
        """Add all Global Favorites items to cart"""
        try:
            logger.info("Adding Global Favorites items to cart...")
            
            # Common Global Favorites items (may vary by location)
            global_favorites_items = [
                "Samurai Pork Burger",
                "McRice Burger",
                "Stroopwafel McFlurry",
                "Banana Pie",
                "Sweet Potato Fries",
                "Taro Pie"
            ]
            
            added_items = []
            
            # Look for add buttons or item cards
            item_selectors = [
                "[data-testid*='menu-item']",
                ".menu-item",
                "[data-testid*='add-item']",
                "button[aria-label*='Add']"
            ]
            
            # Scroll through the menu to find items
            for scroll_position in range(0, 3000, 500):
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(1)
                
                # Look for items to add
                try:
                    add_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Add') or contains(text(), '+') or contains(@data-testid, 'add')]")
                    
                    for button in add_buttons:
                        try:
                            # Check if this is in the Global Favorites section
                            item_container = button.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@data-testid, 'item')]")
                            item_text = item_container.text.lower()
                            
                            # Look for Global Favorites keywords or items
                            if any(item.lower() in item_text for item in global_favorites_items) or 'global' in item_text:
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)
                                button.click()
                                time.sleep(2)
                                
                                # Handle any customization popups
                                self.handle_customization_popup()
                                
                                added_items.append(item_text)
                                logger.info(f"Added item to cart: {item_text[:50]}...")
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
            
            # If no specific Global Favorites found, add some popular international items
            if not added_items:
                logger.info("Specific Global Favorites not found, adding available international items...")
                self.add_available_items(5)  # Add 5 random items
            
            logger.info(f"Total items added: {len(added_items)}")
            return len(added_items) > 0
            
        except Exception as e:
            logger.error(f"Error adding Global Favorites items: {e}")
            return False
    
    def add_available_items(self, max_items=5):
        """Add available items from the menu"""
        try:
            added_count = 0
            
            # Scroll through menu and add items
            for scroll_pos in range(0, 2000, 400):
                self.driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                time.sleep(1)
                
                add_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Add') or contains(text(), '+')]")
                
                for button in add_buttons[:2]:  # Add max 2 items per scroll
                    if added_count >= max_items:
                        break
                        
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        button.click()
                        time.sleep(2)
                        
                        self.handle_customization_popup()
                        added_count += 1
                        logger.info(f"Added item {added_count}")
                        
                    except:
                        continue
                        
                if added_count >= max_items:
                    break
                    
        except Exception as e:
            logger.error(f"Error adding available items: {e}")
    
    def handle_customization_popup(self):
        """Handle item customization popups"""
        try:
            # Look for "Add to Cart" or "Done" buttons in popups
            popup_buttons = [
                "button:contains('Add to Cart')",
                "button:contains('Done')",
                "button:contains('Add')",
                "[data-testid*='add-to-cart']"
            ]
            
            for selector in popup_buttons:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Add to Cart') or contains(text(), 'Done') or contains(text(), 'Add')]"))
                    )
                    button.click()
                    time.sleep(1)
                    break
                except TimeoutException:
                    continue
                    
        except Exception as e:
            logger.debug(f"No customization popup found: {e}")
    
    def view_cart_and_checkout(self):
        """View cart and proceed to checkout"""
        try:
            logger.info("Proceeding to cart and checkout...")
            
            # Look for cart button
            cart_selectors = [
                "[data-testid*='cart']",
                "button:contains('Cart')",
                "[aria-label*='cart']",
                ".cart-button",
                "button:contains('View cart')"
            ]
            
            for selector in cart_selectors:
                try:
                    cart_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    cart_button.click()
                    time.sleep(3)
                    logger.info("Opened cart")
                    break
                except:
                    continue
            
            # Look for checkout button
            checkout_selectors = [
                "button:contains('Checkout')",
                "button:contains('Go to checkout')",
                "[data-testid*='checkout']"
            ]
            
            for selector in checkout_selectors:
                try:
                    checkout_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Checkout') or contains(text(), 'Go to checkout')]")))
                    logger.info("Found checkout button - ready to proceed")
                    # Note: Not actually clicking checkout to avoid placing real order
                    return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error in checkout process: {e}")
            return False
    
    def run_order_process(self):
        """Run the complete ordering process"""
        try:
            self.setup_driver()
            
            logger.info("Starting McDonald's order process...")
            
            # Step 1: Navigate to Uber Eats and handle popups
            self.navigate_to_ubereats()
            
            # Step 2: Set delivery address
            if not self.set_delivery_address():
                return False
            
            # Step 3: Search for McDonald's
            if not self.search_mcdonalds():
                return False
            
            # Step 4: Find Global Favorites section
            if not self.find_global_favorites_section():
                return False
            
            # Step 5: Add Global Favorites items
            if not self.add_global_favorites_items():
                return False
            
            # Step 6: View cart and prepare for checkout
            if not self.view_cart_and_checkout():
                return False
            
            logger.info("Order process completed successfully!")
            logger.info("Note: Actual checkout was not completed to avoid placing a real order")
            
            # Keep browser open for review
            input("Press Enter to close the browser...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in order process: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()

# Main execution
if __name__ == "__main__":
    # Path to your chromedriver executable
    chrome_driver_path = "C:/Users/mcb4339/OneDrive - McDonalds Corp/Desktop/Testing-Area/Selenium/chromedriver.exe"
    
    # Create and run the order bot
    order_bot = McDonaldsOrderBot(chrome_driver_path)
    success = order_bot.run_order_process()
    
    if success:
        print("Order process completed successfully!")
    else:
        print("Order process encountered issues. Please check the logs.")
