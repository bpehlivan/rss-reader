sample_parser_response_fail = {
    "bozo": 1,
    "entries": [],
    "feed": {
        "html": {"lang": "en"},
        "meta": {"name": "viewport", "content": ""},
        "style": {"nonce": "UT2y_g5WN0yXQ3k7gN0rxg"},
        "main": {"id": "af-error-container", "role": "main"},
        "a": {"href": "//www.google.com"},
        "span": {"id": "logo", "aria-label": "Google", "role": "img"}
    },
    "headers": {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "no-cache, no-store, max-age=0, must-revalidate",
        "pragma": "no-cache",
        "expires": "Mon, 01 Jan 1990 00:00:00 GMT",
        "date": "Sun, 10 Mar 2024 13:15:13 GMT",
        "content-security-policy": "",
        "accept-ch": "",
        "cross-origin-opener-policy": "same-origin",
        "permissions-policy": "",
        "content-encoding": "gzip",
        "server": "ESF",
        "x-xss-protection": "0",
        "x-content-type-options": "nosniff",
        "alt-svc": 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
        "connection": "close",
        "transfer-encoding": "chunked"
    },
    "href": "https://feeds.feedburner.com/sdkfsd",
    "status": 404,
    "encoding": "utf-8",
    "bozo_exception": "",
    "version": "",
    "namespaces": {}
}


sample_parser_raw_data = """<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/"><channel><title>NU - Algemeen</title><link>https://www.nu.nl/algemeen</link><description>Het laatste nieuws het eerst op NU.nl</description><atom:link href="https://www.nu.nl/rss/Algemeen" rel="self"/><language>nl-nl</language><copyright>Copyright © 2024, NU</copyright><lastBuildDate>Mon, 11 Mar 2024 00:27:55 +0100</lastBuildDate><ttl>60</ttl><atom:logo>https://www.nu.nl/assets/favicon/nu_logo.svg</atom:logo><item><title>Joy Beune geniet op eigen wijze van wereldtitel: 'Moet van Kjeld vaker blij doen'</title><link>https://www.nu.nl/schaatsen/6304705/joy-beune-geniet-op-eigen-wijze-van-wereldtitel-moet-van-kjeld-vaker-blij-doen.html</link><description>Joy Beune sloot een droomseizoen zondag in stijl af. De 24-jarige schaatsster kroonde zich in Inzell voor het eerst tot wereldkampioen allround. "We gaan deze titel zo echt wel even vieren."</description><pubDate>Sun, 10 Mar 2024 18:45:50 +0100</pubDate><guid isPermaLink="false">article-6304705</guid><enclosure length="0" type="image/jpeg" url="https://media.nu.nl/m/rh6xiryacs6o_sqr256.jpg/joy-beune-geniet-op-eigen-wijze-van-wereldtitel-moet-van-kjeld-vaker-blij-doen.jpg"/><category>schaatsen</category><dc:rights>copyright photo: ANP</dc:rights></item><item><title>Weekweerbericht | Na regen komt zonneschijn (en mogelijk weer regen)</title><link>https://www.nu.nl/weerbericht/6304691/weekweerbericht-na-regen-komt-zonneschijn-en-mogelijk-weer-regen.html</link><description>De week start bewolkt en regenachtig. Wie uitkijkt naar de lente, kan vooral op donderdag genieten van het weer. Dan neemt de temperatuur toe en komt de zon regelmatig tevoorschijn. Vanaf vrijdag stijgt de kans op enkele buien opnieuw.</description><pubDate>Sun, 10 Mar 2024 15:21:26 +0100</pubDate><guid isPermaLink="false">article-6304691</guid><enclosure length="0" type="image/jpeg" url="https://media.nu.nl/m/424xkwuadvm9_sqr256.jpg/weekweerbericht-na-regen-komt-zonneschijn-en-mogelijk-weer-regen.jpg"/><category>weerbericht</category><dc:rights>copyright photo: Getty Images</dc:rights></item></channel></rss>"""  # noqa: E501
