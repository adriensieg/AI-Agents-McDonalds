import asyncio
from orchestrator import McDonaldsA2AOrchestrator

async def main():
    orchestrator = McDonaldsA2AOrchestrator()

    await orchestrator.start_system()

    print("\n🔄 Testing manual order...")
    result = await orchestrator.process_user_order("Get me something spicy for lunch")
    print(f"Order result: {result}")

    status = orchestrator.get_system_status()
    print(f"\n📊 System Status: {status}")

    print("\n⏰ System is now running and will automatically order every Wednesday at noon...")
    print("Press Ctrl+C to stop the system")

    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down McDonald's A2A system...")
        await orchestrator.agents["scheduler"].process_message({"command": "stop_scheduling"})

if __name__ == "__main__":
    asyncio.run(main())
