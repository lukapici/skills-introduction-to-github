import psycopg2.extras
import os

sofaDBpass = os.getenv('DB_PASSWORD')
sofaDBconfig = {}

qaDBpass = os.getenv('qaDB_PASSWORD')
qaDBconfig = {}

def fetch_today_campaign():
    conn_sofaDB = psycopg2.connect(sofaDBconfig)
    cursor = conn_sofaDB.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cursor.execute("""select countryiso as country, case when max(("type" = 'app' and ("start" < now() and ("end" > now() or "end" is null) and weight > 0))::int) = 1
                                                          and max(("type" = 'app-odds' and ("start" < now() and ("end" > now() or "end" is null) and weight > 0))::int) = 1 then 3
                                                         when max(("type" = 'app-odds' and ("start" < now() and ("end" > now() or "end" is null) and weight > 0))::int) = 1 then 2
                                                         when max(("type" = 'app' and ("start" < now() and ("end" > now() or "end" is null) and weight > 0))::int) = 1  then 1
                                                         else 0 end as today_campaign from countryoddsprovider group by countryiso order by countryiso""")
    rows = cursor.fetchall()
    conn_sofaDB.close()
    return {row['country']: row['today_campaign'] for row in rows}

def ensure_table_exists():
    conn_qaDB = psycopg2.connect(qaDBconfig)
    cursor = conn_qaDB.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cursor.execute("""create table if not exists countryCampaigns(
                      country text primary key,
                      yesterday_campaign integer,
                      today_campaign integer)""")
    conn_qaDB.commit()
    conn_qaDB.close()

def update_countryCampaigns(today_data):
    conn_qaDB = psycopg2.connect(qaDBconfig)
    cursor = conn_qaDB.cursor()
    cursor.execute("""update countryCampaigns set yesterday_campaign = today_campaign""")
    for country, today_campaign in today_data.items():
        cursor.execute("""insert into countryCampaigns (country, today_campaign)
                          values (%s, %s)
                          on conflict (country)
                          do update set today_campaign = excluded.today_campaign""",
                          (country, today_campaign))
    conn_qaDB.commit()
    conn_qaDB.close()

def main():
    ensure_table_exists()
    today_data = fetch_today_campaign()
    update_countryCampaigns(today_data)

changes = {
    (0, 1): "activated app campaign, no app-odds campaign",
    (0, 2): "activated app-odds campaign, no app campaign",
    (0, 3): "activated app and app-odds campaign",

    (1, 0): "deactivated app campaign, no app-odds campaign",
    (1, 2): "deactivated app campaign, activated app-odds campaign",
    (1, 3): "has app campaign, activated app-odds campaign",

    (2, 0): "deactivated app-odds campaign, no app campaign",
    (2, 1): "deactivated app-odds campaign, activated app campaign",
    (2, 3): "has app-odds campaign, activated app campaign",

    (3, 0): "deactivated app and app-odds campaign",
    (3, 1): "deactivated app-odds campaign, kept app campaign",
    (3, 2): "deactivated app campaign, kept app-odds campaign"
}

if __name__ == '__main__':
    main()
    conn_qaDB = psycopg2.connect(qaDBconfig)
    cursor = conn_qaDB.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""select * from countryCampaigns""")
    countryCampaigns = cursor.fetchall()
    conn_qaDB.close()
    for country in countryCampaigns:
        if country['yesterday_campaign'] != country['today_campaign']:
            change = changes.get((country["yesterday_campaign"], country["today_campaign"]), "unknown")
            print(f"{country['country']}: {change}")






