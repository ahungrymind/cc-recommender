from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import copy

app = FastAPI()

# Allow all origins for development (tighten this in production)
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cc-recommender-flax.vercel.app/"#,
        #"https://app.the-styx.net"  # if you add a custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load card data
with open("cards.json", "r") as f:
    CARDS = json.load(f)

COUPON_TO_QUESTION = {
    "FineDining" : {"question" : "How much would a biannual $150 \"Fine Dining\" Credit be worth to you? (0-150)", "multiplier" : 2},
    "AppleTV" : {"question" : "An annual AppleTV+ and Apple Music is valued at $250. How much would you be willing to pay for it? (0-250)", "multiplier" : 1},
    "DoorDash+" : {"question" : "A DashPass (DoorDash subscription) is valued at $120 per year. How much would you be willing to pay for it? (0-120)", "multiplier" : 1},
    "DoorDashPromo1" : {"question" : "How much would a monthly $25 DoorDash credit be worth to you? (0-25)", "multiplier" : 12},
    "DoorDashPromo2" : {"question" : "How much would a monthly $10 DoorDash credit be worth to you? (0-10)", "multiplier" : 12},
    "Lyft" : {"question" : "How much would a monthly $10 Lyft credit be worth to you? (0-10)", "multiplier" : 12},
    "StubHub" : {"question" : "How much would a biannual $150 StubHub Credit be worth to you? (0-150)", "multiplier" : 2},
    "Peloton" : {"question" : "How much would a monthly $10 Peloton Credit be worth to you? (0-10)", "multiplier" : 12},
    "StreamingServices" : {"question" : "How much would a monthly $20 general Streaming Services Credit be worth to you? (0-20)", "multiplier" : 12},
    "DisneyBundle" : {"question" : "How much would a monthly $7 Disney Bundle Credit be worth to you? (0-7)", "multiplier" : 12},
    "UberPromo2" : {"question" : "How much would a monthly $15 Uber Cash credit be worth to you? (0-15)", "multiplier" : 12},
    "UberPromo1" : {"question" : "How much would a monthly $10 Uber Cash credit be worth to you? (0-10)", "multiplier" : 12},
    "Walmart+" : {"question" : "Walmart+ is valued at $98 per year ($12.95/month). How much would you be willing to pay for it? (0-98)", "multiplier" : 1},
    "Saks" : {"question" : "How much would a biannual $50 Saks gift card be worth to you? (0-50)", "multiplier" : 2},
    "Dunkin" : {"question" : "How much would a monthly $7 Dunkin Donuts credit be worth to you? (0-7)", "multiplier" : 12},
    "AirlineIncidentals" : {"question" : "On average, how much do you spend on Airline Incidentals each year?", "multiplier" : 1},
    "Hotel" : {"question": "On average, how much do you spend on hotels each year?", "multiplier" : 1}
}

HOTEL_COUPON_KEYS = {"Hotel"} # maybe add "FancyHotels" later
TRAVEL_COUPON_KEYS = {"Travel"}

# Request model expects only `answers`
class ScoreRequest(BaseModel):
    answers: dict
    owned_cards: List[str] = []

@app.get("/cards")
def get_cards():
    return CARDS

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

def estimate_spending(answers):

    rent = 12*int(answers.get("How much do you pay in rent each month?") or 0)
    dining = 12*int(answers.get("On average, how much do you spend on Dining each month?") or 0)
    groceries = 12*int(answers.get("On average, how much do you spend on groceries each month? (excluding Costco)") or 0)
    onlinegroceries = int(answers.get("Given no additional costs, what percentage of your grocery spending are you comfortable doing online?") or 0)
    gas = 12*int(answers.get("On average, how much do you spend on Gas each month?") or 0)
    transit = 12*int(answers.get("On average, how much do you spend on Transit each month? (Trains, Taxi cabs, Ride share services, Ferries, Tolls, Parking, Buses, Subways)") or 0)
    entertainment = int(answers.get("On average, how much do you spend on entertainment each year?") or 0)
    streamingservices = 12*int(answers.get("On average, how much do you spend on Streaming Services each month?") or 0)
    flights = int(answers.get("On average, how much do you spend on flights each year?") or 0)
    hotels = int(answers.get("On average, how much do you spend on hotels each year?") or 0)
    onlineshopping = int(answers.get("On average, how much do you spend on Online Shopping each year?") or 0)
    drugstore = 12*int(answers.get("On average, how much do you spend at the Drug Store each month?") or 0)
    costco = 12*int(answers.get("On average, how much do you spend at Costco each month?") or 0)
    other = 12*int(answers.get("On average, how much do you spend on other expenses not listed so far each month?") or 0)
    expenses3 = 12*int(answers.get("How much do you intend to spend on expected large expenses in the next 3 months?") or 0)
    expenses6 = 12*int(answers.get("How much do you intend to spend on expected large expenses in the next 6 months?") or 0)

    estimated_spending = {
        "Rent": rent,
        "Dining": dining,
        "Groceries": groceries,
        "Gas": gas,
        "Transit": transit,
        "Entertainment": entertainment,
        "StreamingServices": streamingservices,
        "Travel": flights+hotels,
        "OnlineRetail": onlineshopping,
        "Costco": costco,
        "DrugStore": drugstore,
        "OnlineGroceries": onlinegroceries,
        "Others": (other+expenses3+expenses6)
    }

    return estimated_spending, hotels, onlinegroceries

def set_initial_values(cards):
    for card in cards:
        card["score"] = -card["annual_fee"]*100

def apply_owned_coupons(owned_cards, cards, answers, estimated_spending, hotels):
    for card_name in owned_cards:
        card = next((c for c in cards if c["name"] == card_name), None)
        if not card: continue

        score = card["score"]

        for coupon in card.get("coupons", {}):
            coupon_value = safe_int(card["coupons"][coupon])

            if coupon in HOTEL_COUPON_KEYS:
                # Only subtract from hotels to avoid affecting flights
                estimated_spending["Travel"] -= min(hotels, coupon_value)
            # TODO: need review when add rental cars question
            elif coupon in TRAVEL_COUPON_KEYS:
                # Subtract general travel credit from total travel
                spend = min(estimated_spending["Travel"], coupon_value)
                estimated_spending["Travel"] -= spend
                score += spend*100
            
            # Value scoring from user input
            question = COUPON_TO_QUESTION.get(coupon, {}).get("question", "")
            multiplier = COUPON_TO_QUESTION.get(coupon, {}).get("multiplier", 0)
            user_value = safe_int(answers.get(question)) * multiplier * 100
            card_credit = coupon_value * 100

            score += min(user_value, card_credit)
            card["score"] = score

def owned_cards_category_bonus(owned_cards, estimated_spending):
    max_bonus = {}
    for category in estimated_spending:
        best_card = None
        best_rate = 0.0
        for card_name in owned_cards:
            card = next((c for c in CARDS if c["name"] == card_name), None)
            if card:
                bonus = card.get("bonus", {}).get(category, card["default_bonus"])
                if bonus > best_rate:
                    best_rate = bonus
                    best_card = card_name
        if best_card:
            max_bonus[category] = {best_card: best_rate}

    return max_bonus

def adjust_online_groceries(card, spending, onlinegroceries):
    if "Groceries" in spending and "OnlineGroceries" in card["bonus"]:
        grocery_total = spending["Groceries"]
        online_pct = onlinegroceries  # already an integer from earlier

        bonus_online = card["bonus"].get("OnlineGroceries", card["default_bonus"])
        bonus_regular = card["bonus"].get("Groceries", card["default_bonus"])

        if bonus_online > bonus_regular:
            online_share = grocery_total * online_pct // 100
            spending["OnlineGroceries"] = online_share
            spending["Groceries"] = grocery_total - online_share
        else:
            spending["OnlineGroceries"] = 0  # fallback just in case

def score_coupons(card, answers, spending, score, hotels):
    for coupon in card.get("coupons", {}):
        coupon_value = safe_int(card["coupons"][coupon])

        if coupon in HOTEL_COUPON_KEYS:
            # Only subtract from hotels to avoid affecting flights
            spending["Travel"] -= min(hotels, coupon_value)
        # TODO: need review when add rental cars question
        elif coupon in TRAVEL_COUPON_KEYS:
            # Subtract general travel credit from total travel
            spend = min(spending["Travel"], coupon_value)
            spending["Travel"] -= spend
            score += spend*100

        # Value scoring from user input
        question = COUPON_TO_QUESTION.get(coupon, {}).get("question", "")
        multiplier = COUPON_TO_QUESTION.get(coupon, {}).get("multiplier", 0)
        user_value = safe_int(answers.get(question)) * multiplier * 100
        card_credit = coupon_value * 100

        score += min(user_value, card_credit)

    return score

def score_spendings(card, owned_cards, max_bonus, spending, score):
    bonus_caps = card.get("bonus_caps", {})
    for category, amount in spending.items():
        # Determine the card's multiplier for this category
        card_multiplier = card["bonus"].get(category, card["default_bonus"])

        # Check if the user already owns a better (or equal) card for this category
        max_owned_entry = max_bonus.get(category)
        best_owned_multiplier = list(max_owned_entry.values())[0] if max_owned_entry else 0
        best_card_name = list(max_owned_entry.keys())[0] if max_owned_entry else None

        # If this card is not owned and its bonus is less than or equal to best owned card, skip
        if card["name"] not in owned_cards and card_multiplier <= best_owned_multiplier:
            continue

        # If this card is owned, but it's not the best-owned card in this category, skip
        if card["name"] in owned_cards and card["name"] != best_card_name:
            continue

        # If we got here, this card offers a higher multiplier than any owned card
        if category in bonus_caps:
            cap_limit = bonus_caps[category]
            cap_multiplier = card_multiplier
            default_multiplier = card["default_bonus"]

            capped = min(amount, cap_limit)
            uncapped = max(0, amount - cap_limit)

            if card["name"] not in owned_cards:
                score += capped * (cap_multiplier-best_owned_multiplier)
                score += uncapped * (default_multiplier-best_owned_multiplier)
            else:
                score += capped * cap_multiplier
                score += uncapped * default_multiplier
        else:
            if card["name"] not in owned_cards:
                score += amount * (card_multiplier-best_owned_multiplier)
            else:
                score += amount * card_multiplier

    return score


@app.post("/score")
def calculate_scores(data: ScoreRequest):
    answers = data.answers
    owned_cards = data.owned_cards
    cards = copy.deepcopy(CARDS)

    estimated_spending, hotels, onlinegroceries = estimate_spending(answers)
    set_initial_values(cards)

    apply_owned_coupons(owned_cards, cards, answers, estimated_spending, hotels)
    max_bonus = owned_cards_category_bonus(owned_cards, estimated_spending)

    def calc_score(card):
        score = card["score"]
        spending = estimated_spending.copy()
        adjust_online_groceries(card, spending, onlinegroceries)

        score = score_coupons(card, answers, spending, score, hotels)
        score = score_spendings(card, owned_cards, max_bonus, spending, score)

        return round(score, 2)/100

    # Score each card
    results = []
    for card in cards:
        results.append({
            "name": card["name"],
            "image_path": card["image_path"],
            "annual_fee": card["annual_fee"],
            "score": calc_score(card)
    })

    # 🔁 Sort by highest score
    results.sort(key=lambda c: c["score"], reverse=True)

    return results
