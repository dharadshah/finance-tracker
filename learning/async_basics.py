import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


async def save_transaction(description, amount):
    logger.info(f"Saving transaction: {description}")
    await asyncio.sleep(1)           # simulates DB write
    logger.info(f"Transaction saved: {description}")
    return {"description": description, "amount": amount, "saved": True}


async def calculate_balance(transactions):
    logger.info("Calculating balance...")
    await asyncio.sleep(0.5)         # simulates DB aggregation query
    balance = sum(t["amount"] for t in transactions)
    logger.info(f"Balance calculated: Rs.{balance}")
    return balance


async def main():
    # Save multiple transactions concurrently
    results = await asyncio.gather(
        save_transaction("Salary", 50000),
        save_transaction("Netflix", 649),
        save_transaction("Grocery", 2500)
    )

    # Then calculate balance
    balance = await calculate_balance(results)
    print(f"\nFinal Balance: Rs.{balance:.2f}")


asyncio.run(main())