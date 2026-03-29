import React, { useState } from "react";
import "./MyFeedForm.css";
import MyFeed from "./MyFeed";

// Step order
const steps = [
  "user_type",
  "interests",
  "investments",
  "news_type",
  "frequency",
  "goal"
];

export default function MyFeedForm() {
  // ---------------- State ----------------
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState("next");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    user_type: "",
    user_type_other: "",
    interests: [],
    investments: [],
    news_type: "",
    frequency: "",
    goal: ""
  });

  // ---------------- Navigation ----------------
  // Move to next step (with forward animation)
  const nextStep = () => {
    setDirection("next");
    setStep((prev) => Math.min(prev + 1, steps.length - 1));
  };
  // Move to previous step (with backward animation)
  const prevStep = () => {
    setDirection("prev");
    setStep((prev) => Math.max(prev - 1, 0));
  };

  // ---------------- Handle Radio ----------------
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // ---------------- Handle Checkbox ----------------
  // Handles single-select inputs (radio buttons)
  // Updates formData with selected value
  const handleCheckbox = (e) => {
    const { name, value, checked } = e.target;
    const current = formData[name];

    if (checked) {
      // Max 3 only for interests
      if (name === "interests" && current.length >= 3) {
        alert("You can select max 3 options");
        return;
      }

      const updated = [...current, value];
      setFormData({ ...formData, [name]: updated });
    } else {
      const updated = current.filter((item) => item !== value);
      setFormData({ ...formData, [name]: updated });
    }
  };

  // ---------------- Submit ----------------
  // Sends user data to backend API
  // Receives recommended categories based on user profile
  // Stores result for rendering personalized feed

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      setResult(data);
        } 
    catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  // ---------------- Progress ----------------
  const progressPercent = ((step + 1) / steps.length) * 100;

  // ---------------- Step UI ----------------
  // Renders UI dynamically based on current step
  // Each case corresponds to one onboarding question
  const renderStep = () => {
    switch (steps[step]) {
      case "user_type":
        return (
          <>
            <h2>What best describes you?</h2>
            {radioGroup("user_type", [
              "Student",
              "Working professional",
              "Business owner / Founder",
              "Investor",
              "Trader (Stocks / Crypto)",
              "Job seeker",
              "Content creator",
              "Other"
            ])}
          </>
        );

      case "interests":
        return (
          <>
            <h2>Select 2-3 interests</h2>
            {checkboxGroup("interests", [
              "Stock market",
              "Mutual funds",
              "Startups",
              "Business news",
              "Personal finance",
              "Economy"
            ])}
          </>
        );

      case "investments":
        return (
          <>
            <h2>Select any investment types</h2>
            {checkboxGroup("investments", [
              "Stocks",
              "Mutual funds",
              "Not yet"
            ])}
          </>
        );

      case "news_type":
        return (
          <>
            <h2>What type of news do you prefer?</h2>
            {radioGroup("news_type", [
              "Quick updates",
              "Detailed analysis",
              "Simple explainers"
            ])}
          </>
        );

      case "frequency":
        return (
          <>
            <h2>How often do you follow news?</h2>
            {radioGroup("frequency", ["Daily", "Occasionally", "Rarely"])}
          </>
        );

      case "goal":
        return (
          <>
            <h2>What is your goal with news?</h2>
            {radioGroup("goal", [
              "Grow money",
              "Learn basics",
              "Stay updated",
              "Track my investments"
            ])}
          </>
        );

      default:
        return null;
    }
  };

  // ---------------- UI Components ----------------

  const checkboxGroup = (name, options) => (
    <div className="group">
      {options.map((opt) => (
        <label key={opt} className="card">
          <input
            type="checkbox"
            name={name}
            value={opt}
            checked={formData[name].includes(opt)}
            onChange={handleCheckbox}
          />
          {opt}
        </label>
      ))}
    </div>
  );

  const radioGroup = (name, options) => (
    <div className="group">
      {options.map((opt) => (
        <label key={opt} className="card">
          <input
            type="radio"
            name={name}
            value={opt}
            checked={formData[name] === opt}
            onChange={handleChange}
          />
          {opt}
        </label>
      ))}
    </div>
  );

  // ---------------- Loading ----------------
  if (loading) {
    return <div className="container">Loading your personalized feed...</div>;
  }

  // ---------------- Result ----------------
  if (result) {
    return (
        <MyFeed
            categories={result.recommended_categories}
            articles={result.articles}
        />
    );
   }

  // ---------------- Main Render ----------------
  return (
    <div className="container">
      {/* Progress Bar */}
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Step Content */}
      <div
        className={`step ${
          direction === "next" ? "slide-in" : "slide-back"
        }`}
      >
        {renderStep()}
      </div>

      {/* Navigation */}
      <div className="nav">
        {/* Back */}
        {step > 0 && (
          <button onClick={prevStep} className="btn secondary">
            Back
          </button>
        )}

        {/* Next */}
        {step < steps.length - 1 && (
          <button
            onClick={nextStep}
            className="btn"
            disabled={
              steps[step] === "interests" &&
              formData.interests.length < 2
            }
          >
            Next
          </button>
        )}

        {/* Submit */}
        {step === steps.length - 1 && (
          <button onClick={handleSubmit} className="btn">
            Submit
          </button>
        )}
      </div>
    </div>
  );
}