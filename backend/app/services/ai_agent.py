import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Product, Inventory, Order

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "MOCK_KEY"))

# Use a specific model
MODEL_NAME = 'gemini-1.5-pro'

class InventoryAgent:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(MODEL_NAME)
        except Exception as e:
            self.model = None
            print(f"Failed to load AI model: {e}")

    async def analyze_inventory(self, session: AsyncSession):
        """Analyzes the current inventory and returns insights."""
        result = await session.execute(
            select(Product, Inventory).join(Inventory, Product.id == Inventory.product_id)
        )
        data = result.all()
        
        inventory_context = []
        for p, inv in data:
            inventory_context.append({
                "product_name": p.name,
                "current_stock": inv.current_stock,
                "threshold": inv.threshold,
                "daily_velocity_estimate": 2.5 # Mock velocity
            })
            
        prompt = f"""
        You are an expert Inventory Intelligence Engine for an SME.
        Analyze the following inventory data and provide actionable insights.
        Return ONLY a JSON array containing objects with:
        - "product_name"
        - "status" (Critical, Warning, Healthy)
        - "predicted_depletion_days" (integer)
        - "restock_recommendation" (amount to restock, integer)
        - "reason" (short string explaining why)
        
        Data: {json.dumps(inventory_context)}
        """
        
        if not self.model or os.getenv("GEMINI_API_KEY") == "MOCK_KEY":
            # Mock response if no API key
            return [
                {
                    "product_name": "Organik Domates Salçası",
                    "status": "Critical",
                    "predicted_depletion_days": 2,
                    "restock_recommendation": 50,
                    "reason": "Stock is below threshold and sales velocity is high."
                }
            ]
            
        try:
            response = self.model.generate_content(prompt)
            # In a real app, parse the JSON robustly
            # For now we'll assume it returns clean JSON
            content = response.text
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"AI Generation error: {e}")
            return []

class CustomerSupportAgent:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(MODEL_NAME)
        except:
            self.model = None

    async def handle_query(self, query: str, session: AsyncSession) -> str:
        # Mock RAG: Fetch basic info
        result = await session.execute(select(Order).limit(5))
        orders = result.scalars().all()
        order_context = [{"id": o.id, "customer": o.customer_name, "status": o.status} for o in orders]
        
        prompt = f"""
        You are a helpful customer support AI for an SME. 
        Answer the customer's query using ONLY the provided context. If you don't know, say so politely.
        
        Context (Recent Orders): {json.dumps(order_context)}
        
        Customer Query: "{query}"
        """
        
        if not self.model or os.getenv("GEMINI_API_KEY") == "MOCK_KEY":
             return "I can help with that! However, my AI brain is currently in mock mode because the Gemini API key is missing."
             
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Sorry, I am currently unable to process your request."

inventory_agent = InventoryAgent()
support_agent = CustomerSupportAgent()
