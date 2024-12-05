import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_smart_analysis():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/auth/status") as response:
                status = await response.json()
                logger.info(f"Auth Status: {status}")

                if status.get('status') == 'disconnected':
                    async with session.post("http://localhost:8000/auth/refresh") as auth_response:
                        auth_result = await auth_response.json()
                        logger.info(f"Auth refresh result: {auth_result}")

            async with session.get("http://localhost:8000/analysis/smart") as response:
                if response.status == 200:
                    analysis = await response.json()
                    print("\nSmart Analysis:")
                    print(json.dumps(analysis, indent=2))
                else:
                    error_text = await response.text()
                    logger.error(f"Error {response.status}: {error_text}")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_smart_analysis()) 