import React, { useEffect, useState } from "react";
import "./App.css";

// Tabs with only questions (no spending inputs)
const categoryTabs = [
  {
    label: "Preliminaries",
    questions: [
      {
        prompt: "Do you currently own any credit cards?",
        type: "yesno",
        explain: ""
      },
      {
        prompt: "What is your Credit Score?",
        type: "text",
        explain: ""
      },
    ]
  },
  {
    label: "Rent",
    questions: [
      {
        prompt: "How much do you pay in rent each month?",
        type: "text",
        explain: ""
      }
    ]
  },
  {
    label: "Food & Dining",
    questions: [
      {
        prompt: "On average, how much do you spend on Dining each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on groceries each month? (excluding Costco)",
        type: "text",
        explain: ""
      },
      {
        prompt: "Given no additional costs, what percentage of your grocery spending are you comfortable doing online? (0-100)",
        type: "text",
        explain: ""
      },
      {
        prompt: "Walmart+ is valued at $98 per year ($12.95/month). How much would you be willing to pay for it? (0-98)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a biannual $150 \"Fine Dining\" Credit be worth to you? (0-150)",
        type: "text",
        explain: "https://www.opentable.com/c/chasedining/"
      },
      {
        prompt: "A DashPass (DoorDash subscription) is valued at $120 per year. How much would you be willing to pay for it? (0-120)",
        type: "text",
        explain: "Includes $0 delivery fees and lower service fees on eligible DoorDash orders."
      },
      {
        prompt: "How much would a monthly $10 DoorDash credit be worth to you? (0-10)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $25 DoorDash credit be worth to you? (0-25)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $7 Dunkin Donuts credit be worth to you? (0-7)",
        type: "text",
        explain: "If you purchase $7 of Dunkin Donuts every month, it would be worth $7 to you. If you would never use it, it's worth $0."
      }
    ]
  },
  {
    label: "Transportation",
    questions: [
      {
        prompt: "On average, how much do you spend on Gas each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on Transit each month? (Trains, Taxi cabs, Ride share services, Ferries, Tolls, Parking, Buses, Subways)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $10 Lyft credit be worth to you? (0-10)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $10 Uber Cash credit be worth to you? (0-10)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $15 Uber Cash credit be worth to you? (0-15)",
        type: "text",
        explain: ""
      }
    ]
  },
  {
    label: "Entertainment",
    questions: [
      {
        prompt: "On average, how much do you spend on entertainment each year?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on Streaming Services each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $20 general Streaming Services Credit be worth to you? (0-20)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $7 Disney Bundle Credit be worth to you? (0-7)",
        type: "text",
        explain: ""
      },
      {
        prompt: "An annual AppleTV+ and Apple Music is valued at $250. How much would you be willing to pay for it? (0-250)",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a biannual $150 StubHub Credit be worth to you? (0-150)",
        type: "text",
        explain: ""
      },
    ]
  },
  {
    label: "Travel",
    questions: [
      {
        prompt: "On average, how much do you spend on flights each year?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on hotels each year?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on Airline Incidentals each year?",
        type: "text",
        explain: ""
      },
    ]
  },
  {
    label: "Shopping",
    questions: [
      {
        prompt: "On average, how much do you spend on Online Shopping each year?",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a biannual $50 Saks gift card be worth to you? (0-50)",
        type: "text",
        explain: ""
      }
    ]
  },
  {
    label: "Other",
    questions: [
      {
        prompt: "On average, how much do you spend at the Drug Store each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend at Costco each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "On average, how much do you spend on other expenses not listed so far each month?",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much would a monthly $10 Peloton Credit be worth to you? (0-10)",
        type: "text",
        explain: ""
      }
    ]
  },
  {
    label: "Large Expenses",
    questions: [
      {
        prompt: "How much do you intend to spend on expected large expenses in the next 3 months?",
        type: "text",
        explain: ""
      },
      {
        prompt: "How much do you intend to spend on expected large expenses in the next 6 months?",
        type: "text",
        explain: ""
      }
    ]
  }
];

export default function App() {
  const [cards, setCards] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentTab, setCurrentTab] = useState(0);
  const [scoredCards, setScoredCards] = useState([]);
  const [ownedCards, setOwnedCards] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/cards")
      .then(res => res.json())
      .then(setCards);
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers, owned_cards: ownedCards }),
    })
      .then(res => res.json())
      .then(setScoredCards);
  }, [answers, ownedCards]); 

  return (
    <div className="container">
      <h1>Credit Card Advisor</h1>

      <div className="non-sticky-scroll-wrapper">
        <h2>Cards You Own</h2>
        <CardScrollRow
          cards={ownedCards
            .map(name =>
              scoredCards.find(c => c.name === name) ||
              cards.find(c => c.name === name)
            )
            .filter(Boolean)
          }

          toggleOwned={name =>
            setOwnedCards(prev => prev.filter(c => c !== name))
          }
          owned={true}
        />
      </div>


      <div className="sticky-scroll-wrapper">
        <h2>Recommended Cards</h2>
        <CardScrollRow
          cards={scoredCards.filter(c => !ownedCards.includes(c.name))}
          toggleOwned={name =>
            setOwnedCards(prev => [...prev, name])
          }
          owned={false}
        />
      </div>

      <CategoryTabs
        categories={categoryTabs}
        answers={answers}
        setAnswers={setAnswers}
        current={currentTab}
        setCurrent={setCurrentTab}
      />
    </div>
  );


}

function CardScrollRow({ cards, toggleOwned, owned }) {
  return (
    <div className="scroll-row">
      {cards.map((card) => {
        const additionalValue = "score" in card ? card.score : 0;
        const annualFee = card.annual_fee ?? 0;
        const totalValue = (additionalValue + annualFee).toFixed(2);

        return (
          <div className="card-box" key={card.name}>
            <div className="card-name">
              {card.name}
              <input
                type="checkbox"
                checked={owned}
                onChange={() => toggleOwned(card.name)}
                style={{ float: "right" }}
                title={owned ? "Unmark as owned" : "Mark as owned"}
              />
            </div>
            <div className="card-content">
              <img src={card.image_path} alt={card.name} />
              <div className="card-info">
                {"score" in card && (
                  <>
                    <p>
                      <strong>{owned ? "Value" : "Value Added"}:</strong> {additionalValue.toFixed(2)}
                    </p>
                    <p>Annual Fee: ${annualFee}</p>
                    <p>Value w/o Fee: {totalValue}</p>
                  </>
                )}
                {!("score" in card) && (
                  <p>Annual Fee: ${annualFee}</p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}




function CategoryTabs({ categories, answers, setAnswers, current, setCurrent }) {
  const active = categories[current];

  const handleAnswerChange = (q, value) => {
    setAnswers((prev) => ({ ...prev, [q]: value }));
  };

  return (
    <div className="question-section">
      <div className="sticky-tab-wrapper">
        <div className="question-tabs">
          {categories.map((cat, i) => (
            <div
              key={i}
              className={`question-tab ${i === current ? "active" : ""}`}
              onClick={() => setCurrent(i)}
            >
              {cat.label}
            </div>
          ))}
        </div>
      </div>


      <div className="category-box">
        {active.questions.length > 0 && (
          <div className="question-box">
            {active.questions.map((q, idx) => (
              <div key={idx} className="single-question">
                <p>{q.prompt}</p>
                <div className="answer-options">
                  {q.type === "yesno" ? (
                    <>
                      <label>
                        <input
                          type="radio"
                          name={`answer-${current}-${idx}`}
                          value="yes"
                          checked={answers[q.prompt] === "yes"}
                          onChange={(e) => handleAnswerChange(q.prompt, e.target.value)}
                        />
                        Yes
                      </label>
                      <label>
                        <input
                          type="radio"
                          name={`answer-${current}-${idx}`}
                          value="no"
                          checked={answers[q.prompt] === "no"}
                          onChange={(e) => handleAnswerChange(q.prompt, e.target.value)}
                        />
                        No
                      </label>
                    </>
                  ) : (
                    <input
                      type="number"
                      min="0"
                      step="1"
                      placeholder="0"
                      value={answers[q.prompt] || ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        handleAnswerChange(q.prompt, val === "" ? "" : parseInt(val, 10));
                      }}
                    />

                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
