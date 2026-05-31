import asyncio
from app.database import AsyncSessionFactory
from sqlalchemy import select
from app.models import EmailAccount
from app.tasks.email_tasks import _sync_google_account, _sync_outlook_account, _sync_imap_account

async def main():
    async with AsyncSessionFactory() as db:
        accounts = (await db.execute(select(EmailAccount))).scalars().all()
        for account in accounts:
            if account.provider == 'google':
                await _sync_google_account(db, account)
            elif account.provider == 'outlook':
                await _sync_outlook_account(db, account)
            else:
                await _sync_imap_account(db, account)
        await db.commit()
    print('Done!')

if __name__ == "__main__":
    asyncio.run(main())
