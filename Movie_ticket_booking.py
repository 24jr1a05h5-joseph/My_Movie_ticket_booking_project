
import os
import datetime as dt
import random
import string
from typing import Dict, List, Optional

import streamlit as st

# ============================================================
# CINEBOOK - LIVE MOVIE DISCOVERY + BOOKING DEMO
# ============================================================
# Movie data:
#   TMDB /discover/movie with India region + release-date filters.
#
# Important:
#   TMDB provides movie metadata/posters/release dates.
#   It does NOT provide live theatre seat inventory.
#   Theatre/showtime/seat data below is YOUR APP'S booking inventory.
#   For truly live theatre seats, connect an authorised cinema/ticketing API.
# ============================================================

st.set_page_config(
    page_title="CineBook",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TODAY = dt.datetime.now(IST).date()

# No API token is required in this version.

LANGUAGES = {
    "all": "All Languages",
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
}

CITIES = [
    "Hyderabad",
    "Vijayawada",
    "Guntur",
    "Visakhapatnam",
    "Warangal",
    "Bengaluru",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Pune",
    "Kolkata",
]

# This is local application inventory, not claimed as live BMS inventory.
THEATRES = {
    "Hyderabad": [
        ("AMB Cinemas", "Gachibowli"),
        ("PVR INOX", "Banjara Hills"),
        ("Cinepolis", "Mantra Mall"),
        ("Prasads Multiplex", "Necklace Road"),
    ],
    "Vijayawada": [
        ("PVR INOX", "LEPL Centro"),
        ("Cinepolis", "PVP Square"),
        ("Trendset Cinemas", "Benz Circle"),
    ],
    "Guntur": [
        ("PVR INOX", "Mangalagiri"),
        ("Cinepolis", "Lakshmipuram"),
        ("Sree Rama Cinemas", "Brodipet"),
    ],
    "Visakhapatnam": [
        ("INOX", "Varun Beach"),
        ("Cinepolis", "CBM Compound"),
        ("Melody Theatre", "Dwaraka Nagar"),
    ],
    "Warangal": [
        ("Asian Cinemas", "Hanamkonda"),
        ("INOX", "Warangal"),
        ("Lakshmi Theatre", "Kazipet"),
    ],
    "Bengaluru": [
        ("PVR INOX", "Whitefield"),
        ("Cinepolis", "Bannerghatta"),
        ("Galaxy Cinemas", "Indiranagar"),
    ],
    "Chennai": [
        ("PVR INOX", "Velachery"),
        ("Rohini Silver Screens", "Koyambedu"),
        ("AGS Cinemas", "T Nagar"),
    ],
    "Mumbai": [
        ("PVR INOX", "Andheri"),
        ("Cinepolis", "Andheri West"),
        ("INOX", "Malad"),
    ],
    "Delhi": [
        ("PVR INOX", "Saket"),
        ("Cinepolis", "Janakpuri"),
        ("INOX", "Connaught Place"),
    ],
    "Pune": [
        ("PVR INOX", "Viman Nagar"),
        ("Cinepolis", "Amanora"),
        ("INOX", "Kothrud"),
    ],
    "Kolkata": [
        ("PVR INOX", "Salt Lake"),
        ("Cinepolis", "Acropolis"),
        ("INOX", "South City"),
    ],
}

SHOW_TIMES = [
    "10:00 AM",
    "12:45 PM",
    "03:30 PM",
    "06:15 PM",
    "09:00 PM",
    "11:30 PM",
]

SEAT_ROWS = list("ABCDEFGH")
SEATS_PER_ROW = 10
PRICE = {"Silver": 150, "Gold": 220, "Premium": 300, "Recliner": 450}

# ============================================================
# SESSION
# ============================================================
defaults = {
    "page": "home",
    "city": "Hyderabad",
    "language": "all",
    "movies": [],
    "movies_loaded": False,
    "tmdb_error": "",
    "movie": None,
    "selected_date": TODAY,
    "theatre": None,
    "showtime": None,
    "seats": [],
    "payment": None,
    "ticket": None,
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

ss = st.session_state


# ============================================================
# HELPERS
# ============================================================
def money(value: float) -> str:
    return f"₹{value:,.2f}"


def go(page: str):
    ss.page = page
    st.rerun()


def local_movies(language_code: str = "all") -> List[Dict]:
    """Built-in movie catalog. No API token or internet is required."""
    catalog = [
        {"id": 1, "title": "Pushpa 2: The Rule", "original_title": "Pushpa 2: The Rule",
         "language_code": "te", "release_date": "2024-12-05", "rating": 8.2,
         "overview": "Pushpa continues his journey as he faces new challenges and powerful enemies."},
        {"id": 2, "title": "Devara: Part 1", "original_title": "Devara: Part 1",
         "language_code": "te", "release_date": "2024-09-27", "rating": 7.1,
         "overview": "A powerful story of courage, fear, family and the sea."},
        {"id": 3, "title": "Kalki 2898 AD", "original_title": "Kalki 2898 AD",
         "language_code": "te", "release_date": "2024-06-27", "rating": 8.0,
         "overview": "A futuristic Indian epic set in a world where mythology and science meet."},
        {"id": 4, "title": "RRR", "original_title": "RRR",
         "language_code": "te", "release_date": "2022-03-25", "rating": 8.0,
         "overview": "Two revolutionaries join forces in a story of friendship, courage and sacrifice."},
        {"id": 5, "title": "Salaar: Part 1 – Ceasefire", "original_title": "Salaar: Part 1 – Ceasefire",
         "language_code": "te", "release_date": "2023-12-22", "rating": 7.0,
         "overview": "A violent kingdom, a powerful friendship and a promise lead to an epic conflict."},
        {"id": 6, "title": "Hanu-Man", "original_title": "Hanu-Man",
         "language_code": "te", "release_date": "2024-01-12", "rating": 7.9,
         "overview": "A young man receives extraordinary powers and learns what it means to become a hero."},
        {"id": 7, "title": "Baahubali 2: The Conclusion", "original_title": "Baahubali 2: The Conclusion",
         "language_code": "te", "release_date": "2017-04-28", "rating": 8.2,
         "overview": "The legendary kingdom faces its final battle as the truth behind Baahubali is revealed."},
        {"id": 8, "title": "Jersey", "original_title": "Jersey",
         "language_code": "te", "release_date": "2019-04-19", "rating": 8.5,
         "overview": "A former cricketer tries to return to the sport to fulfill a promise to his son."},
        {"id": 9, "title": "Hi Nanna", "original_title": "Hi Nanna",
         "language_code": "te", "release_date": "2023-12-07", "rating": 8.0,
         "overview": "A heartfelt family story about love, memories and a father and daughter."},
        {"id": 10, "title": "Arjun Reddy", "original_title": "Arjun Reddy",
         "language_code": "te", "release_date": "2017-08-25", "rating": 8.0,
         "overview": "A brilliant but troubled surgeon struggles with love and self-destruction."},
        {"id": 11, "title": "The Greatest of All Time", "original_title": "The Greatest of All Time",
         "language_code": "ta", "release_date": "2024-09-05", "rating": 6.0,
         "overview": "An elite former agent faces a dangerous mission connected to his past."},
        {"id": 12, "title": "Vikram", "original_title": "Vikram",
         "language_code": "ta", "release_date": "2022-06-03", "rating": 8.0,
         "overview": "A special investigation uncovers a dangerous criminal network."},
        {"id": 13, "title": "Leo", "original_title": "Leo",
         "language_code": "ta", "release_date": "2023-10-19", "rating": 7.4,
         "overview": "A quiet cafe owner is pulled into a violent past he tried to leave behind."},
        {"id": 14, "title": "Jawan", "original_title": "Jawan",
         "language_code": "hi", "release_date": "2023-09-07", "rating": 7.4,
         "overview": "A man driven by a personal mission takes on a corrupt system."},
        {"id": 15, "title": "12th Fail", "original_title": "12th Fail",
         "language_code": "hi", "release_date": "2023-10-27", "rating": 8.8,
         "overview": "An inspiring story of determination, education and overcoming difficult circumstances."},
        {"id": 16, "title": "Stree 2", "original_title": "Stree 2",
         "language_code": "hi", "release_date": "2024-08-15", "rating": 7.0,
         "overview": "A supernatural comedy where a small town faces a mysterious new threat."},
        {"id": 17, "title": "Manjummel Boys", "original_title": "Manjummel Boys",
         "language_code": "ml", "release_date": "2024-02-22", "rating": 8.2,
         "overview": "A group of friends find themselves in a dangerous situation during a trip."},
        {"id": 18, "title": "Aavesham", "original_title": "Aavesham",
         "language_code": "ml", "release_date": "2024-04-11", "rating": 7.7,
         "overview": "Three college students meet a local gangster and their lives take an unexpected turn."},
        {"id": 19, "title": "Kantara", "original_title": "Kantara",
         "language_code": "kn", "release_date": "2022-09-30", "rating": 8.2,
         "overview": "A powerful village story blending tradition, conflict and folklore."},
        {"id": 20, "title": "K.G.F: Chapter 2", "original_title": "K.G.F: Chapter 2",
         "language_code": "kn", "release_date": "2022-04-14", "rating": 8.3,
         "overview": "Rocky rises to power while enemies close in around his empire."},
    ]

    if language_code != "all":
        catalog = [m for m in catalog if m["language_code"] == language_code]

    for movie in catalog:
        movie["language"] = LANGUAGES.get(
            movie["language_code"], movie["language_code"].upper()
        )
        movie["poster_bytes"] = None
        movie["poster_url"] = ""

    return catalog


def load_movies(force=False):
    if ss.movies_loaded and not force:
        return

    ss.tmdb_error = ""
    ss.movies = local_movies(ss.language)
    ss.movies_loaded = True


def movies_for_period(kind: str) -> List[Dict]:
    first_this_month = TODAY.replace(day=1)
    if TODAY.month == 12:
        first_next_month = TODAY.replace(year=TODAY.year + 1, month=1, day=1)
    else:
        first_next_month = TODAY.replace(month=TODAY.month + 1, day=1)

    if first_next_month.month == 12:
        first_after_next = first_next_month.replace(
            year=first_next_month.year + 1, month=1, day=1
        )
    else:
        first_after_next = first_next_month.replace(
            month=first_next_month.month + 1, day=1
        )

    if kind == "now":
        # Recent theatrical releases. TMDB does not expose a guaranteed
        # theatre-end date, so this is an API-based "recent theatrical" list.
        cutoff = TODAY - dt.timedelta(days=60)
        return [
            m for m in ss.movies
            if cutoff.isoformat() <= m["release_date"] <= TODAY.isoformat()
        ]

    if kind == "this_month":
        return [
            m for m in ss.movies
            if first_this_month.isoformat() <= m["release_date"] <= TODAY.isoformat()
        ]

    if kind == "next_month":
        return [
            m for m in ss.movies
            if first_next_month.isoformat() <= m["release_date"] < first_after_next.isoformat()
        ]

    if kind == "future":
        return [
            m for m in ss.movies
            if m["release_date"] > TODAY.isoformat()
        ]

    return ss.movies


def format_date(date_string: str) -> str:
    try:
        return dt.date.fromisoformat(date_string).strftime("%d %b %Y")
    except ValueError:
        return date_string


def make_seats(movie_id: int, theatre: str, showtime: str, date_value: dt.date) -> set:
    """
    Deterministic occupied-seat simulation for this app's own inventory.
    It stays the same for the same movie/theatre/show/date.
    """
    seed_text = f"{movie_id}-{theatre}-{showtime}-{date_value.isoformat()}"
    rng = random.Random(seed_text)
    all_seats = [f"{r}{n}" for r in SEAT_ROWS for n in range(1, SEATS_PER_ROW + 1)]
    count = rng.randint(8, 24)
    return set(rng.sample(all_seats, count))


def movie_card(movie: Dict, key_prefix: str):
    if movie.get("poster_bytes"):
        st.image(movie["poster_bytes"], use_container_width=True)
    else:
        st.markdown("### 🎬")
        st.caption("Poster unavailable in offline mode.")
    st.markdown(f"**{movie['title']}**")
    st.caption(
        f"{movie['language']} • {format_date(movie['release_date'])} • "
        f"⭐ {movie['rating']:.1f}"
    )
    if st.button("View Movie", key=f"{key_prefix}_{movie['id']}", use_container_width=True):
        ss.movie = movie
        ss.selected_date = TODAY
        ss.theatre = None
        ss.showtime = None
        ss.seats = []
        go("details")


def show_movie_grid(movies: List[Dict], key_prefix: str, columns=5):
    if not movies:
        st.info("No movies found for this period/filter.")
        return

    for start in range(0, len(movies), columns):
        row = movies[start:start + columns]
        cols = st.columns(len(row))
        for col, movie in zip(cols, row):
            with col:
                movie_card(movie, key_prefix)


def available_dates(movie: Dict) -> List[dt.date]:
    # App booking dates. For a real cinema integration this must come from
    # the theatre/ticketing API's available_dates.
    release = dt.date.fromisoformat(movie["release_date"])
    start = max(TODAY, release)
    return [start + dt.timedelta(days=i) for i in range(0, 30)]


def theatre_inventory(movie: Dict, date_value: dt.date):
    city_theatres = THEATRES.get(ss.city, THEATRES["Hyderabad"])
    items = []

    for theatre_name, location in city_theatres:
        for time_value in SHOW_TIMES:
            occupied = make_seats(movie["id"], theatre_name, time_value, date_value)
            available = len(SEAT_ROWS) * SEATS_PER_ROW - len(occupied)
            items.append(
                {
                    "theatre": theatre_name,
                    "location": location,
                    "time": time_value,
                    "available": available,
                    "occupied": occupied,
                }
            )
    return items


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
    .hero {
        padding: 22px 28px;
        border-radius: 20px;
        background: linear-gradient(135deg, #111827, #312e81);
        color: white;
        margin-bottom: 20px;
    }
    .hero h1 { margin: 0; }
    .hero p { margin: 5px 0 0; opacity: .85; }

    .info-card {
        padding: 18px;
        border-radius: 16px;
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .ticket {
        padding: 25px;
        border-radius: 20px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 30px rgba(0,0,0,.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>🎬 CineBook</h1>
        <p>Live movie discovery → date → theatre → showtime → seats → payment → ticket</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("📍 Location")
    new_city = st.selectbox(
        "City / District",
        CITIES,
        index=CITIES.index(ss.city),
    )
    if new_city != ss.city:
        ss.city = new_city
        ss.page = "home"
        ss.movie = None
        ss.movies_loaded = False
        st.rerun()

    st.divider()
    st.header("🎞️ Movie Data")
    st.success("🟢 Movie data ready")
    st.caption("No TMDB token is required.")

    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        go("home")

load_movies()

# ============================================================
# HOME
# ============================================================
if ss.page == "home":
    st.subheader(f"🎥 Movies in {ss.city}")
    st.caption(
        f"Data date: {TODAY.strftime('%d %B %Y')} • "
        "Movie lists are calculated from the built-in movie catalog."
    )

    # Search
    search = st.text_input("🔎 Search movie", placeholder="Enter movie name...").strip().lower()

    all_movies = ss.movies
    if search:
        all_movies = [
            m for m in all_movies
            if search in m["title"].lower()
            or search in m["original_title"].lower()
        ]

    tabs = st.tabs([
        "🔥 Now Showing",
        "📅 This Month",
        "➡️ Next Month",
        "🚀 Upcoming",
        "🎬 All",
    ])

    with tabs[0]:
        st.caption("Recent releases from the built-in movie catalog.")
        show_movie_grid(
            [m for m in all_movies if m in movies_for_period("now")],
            "now",
        )

    with tabs[1]:
        show_movie_grid(
            [m for m in all_movies if m in movies_for_period("this_month")],
            "thismonth",
        )

    with tabs[2]:
        show_movie_grid(
            [m for m in all_movies if m in movies_for_period("next_month")],
            "nextmonth",
        )

    with tabs[3]:
        show_movie_grid(
            [m for m in all_movies if m in movies_for_period("future")],
            "future",
        )

    with tabs[4]:
        show_movie_grid(all_movies, "all")

# ============================================================
# DETAILS + DATE + THEATRE + SHOW
# ============================================================
elif ss.page == "details":
    movie = ss.movie

    if not movie:
        go("home")

    if st.button("← Back to Movies"):
        go("home")

    st.subheader(movie["title"])

    left, right = st.columns([1, 2])

    with left:
        if movie.get("poster_bytes"):
            st.image(movie["poster_bytes"], use_container_width=True)
        else:
            st.markdown("## 🎬")
            st.info("Poster unavailable in offline mode.")

    with right:
        st.markdown(f"### {movie['title']}")
        st.write(
            f"**Language:** {movie['language']}  \n"
            f"**Release date:** {format_date(movie['release_date'])}  \n"
            f"**Rating:** ⭐ {movie['rating']:.1f}"
        )
        st.write(movie["overview"])

        st.divider()
        st.subheader(f"📅 Select date in {ss.city}")

        dates = available_dates(movie)
        date_labels = [d.strftime("%a, %d %b") for d in dates]

        selected_label = st.selectbox(
            "Date",
            date_labels,
            index=max(
                0,
                dates.index(ss.selected_date) if ss.selected_date in dates else 0,
            ),
        )
        ss.selected_date = dates[date_labels.index(selected_label)]

        st.subheader("🎭 Theatres & Showtimes")

        inventory = theatre_inventory(movie, ss.selected_date)

        for item in inventory:
            c1, c2, c3 = st.columns([2.2, 1.5, 1.2])
            with c1:
                st.write(f"**{item['theatre']}**")
                st.caption(item["location"])
            with c2:
                st.write(f"🕒 {item['time']}")
                st.caption(f"{item['available']} seats available")
            with c3:
                if st.button(
                    "Select",
                    key=f"show_{movie['id']}_{item['theatre']}_{item['time']}",
                    use_container_width=True,
                ):
                    ss.theatre = item["theatre"]
                    ss.showtime = item["time"]
                    ss.seats = []
                    go("seats")

# ============================================================
# SEATS
# ============================================================
elif ss.page == "seats":
    movie = ss.movie

    if not movie or not ss.theatre or not ss.showtime:
        go("home")

    st.subheader("💺 Select Seats")
    st.caption(
        f"{movie['title']} • {ss.city} • {ss.theatre} • "
        f"{ss.selected_date.strftime('%d %b %Y')} • {ss.showtime}"
    )

    occupied = make_seats(
        movie["id"],
        ss.theatre,
        ss.showtime,
        ss.selected_date,
    )

    st.info("Grey = occupied • Green = available • Red = selected")

    for row in SEAT_ROWS:
        cols = st.columns(SEATS_PER_ROW)
        for i, col in enumerate(cols, start=1):
            seat_id = f"{row}{i}"
            with col:
                if seat_id in occupied:
                    st.button(
                        seat_id,
                        disabled=True,
                        key=f"sold_{seat_id}",
                        use_container_width=True,
                    )
                else:
                    selected = seat_id in ss.seats
                    label = f"🔴 {seat_id}" if selected else seat_id
                    if st.button(
                        label,
                        key=f"seat_{seat_id}",
                        use_container_width=True,
                    ):
                        if selected:
                            ss.seats.remove(seat_id)
                        else:
                            ss.seats.append(seat_id)
                        st.rerun()

    st.divider()
    st.write(f"**Selected seats:** {', '.join(ss.seats) if ss.seats else 'None'}")

    category = st.selectbox("Seat category", list(PRICE.keys()))
    total = PRICE[category] * len(ss.seats)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", use_container_width=True):
            go("details")
    with c2:
        if st.button(
            f"Continue • {money(total)}",
            type="primary",
            disabled=not ss.seats,
            use_container_width=True,
        ):
            ss.category = category
            go("payment")

# ============================================================
# PAYMENT
# ============================================================
elif ss.page == "payment":
    movie = ss.movie

    if not movie or not ss.seats:
        go("home")

    st.subheader("💳 Payment")
    subtotal = PRICE[ss.category] * len(ss.seats)
    convenience = 30.0
    total = subtotal + convenience

    st.markdown(
        f"""
        <div class="info-card">
        <b>{movie['title']}</b><br>
        {ss.theatre}, {ss.city}<br>
        {ss.selected_date.strftime('%d %b %Y')} • {ss.showtime}<br>
        Seats: {', '.join(ss.seats)}<br>
        Category: {ss.category}<br><br>
        Ticket amount: {money(subtotal)}<br>
        Convenience fee: {money(convenience)}<br>
        <b>Total: {money(total)}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    method = st.radio(
        "Payment method",
        ["UPI", "Card", "Net Banking"],
        horizontal=True,
    )

    if st.button("💰 Pay & Confirm Booking", type="primary", use_container_width=True):
        booking_id = "CB" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

        ss.ticket = {
            "id": booking_id,
            "movie": movie["title"],
            "city": ss.city,
            "theatre": ss.theatre,
            "date": ss.selected_date.strftime("%d %b %Y"),
            "time": ss.showtime,
            "seats": list(ss.seats),
            "category": ss.category,
            "payment": method,
            "total": total,
        }
        go("ticket")

    if st.button("← Back to Seats", use_container_width=True):
        go("seats")

# ============================================================
# TICKET
# ============================================================
elif ss.page == "ticket":
    ticket = ss.ticket

    if not ticket:
        go("home")

    st.success("🎉 Booking Confirmed!")

    st.markdown(
        f"""
        <div class="ticket">
            <h2>🎬 CINEBOOK</h2>
            <hr>
            <h3>{ticket['movie']}</h3>
            <b>Booking ID:</b> {ticket['id']}<br><br>
            <b>City:</b> {ticket['city']}<br>
            <b>Theatre:</b> {ticket['theatre']}<br>
            <b>Date:</b> {ticket['date']}<br>
            <b>Time:</b> {ticket['time']}<br>
            <b>Seats:</b> {', '.join(ticket['seats'])}<br>
            <b>Category:</b> {ticket['category']}<br>
            <b>Payment:</b> {ticket['payment']}<br><br>
            <h2>Paid: {money(ticket['total'])}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ticket_text = "\n".join([
        "CINEBOOK MOVIE TICKET",
        f"Booking ID: {ticket['id']}",
        f"Movie: {ticket['movie']}",
        f"City: {ticket['city']}",
        f"Theatre: {ticket['theatre']}",
        f"Date: {ticket['date']}",
        f"Time: {ticket['time']}",
        f"Seats: {', '.join(ticket['seats'])}",
        f"Category: {ticket['category']}",
        f"Payment: {ticket['payment']}",
        f"Total: {money(ticket['total'])}",
    ])

    st.download_button(
        "⬇️ Download Ticket",
        ticket_text,
        file_name=f"{ticket['id']}.txt",
        use_container_width=True,
    )

    if st.button("🎬 Book Another Movie", type="primary", use_container_width=True):
        ss.movie = None
        ss.theatre = None
        ss.showtime = None
        ss.seats = []
        ss.ticket = None
        go("home")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Movie metadata and posters: TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB. "
    "Theatre/showtime/seat/payment screens are local app functionality unless connected to an authorised ticketing provider."
)
