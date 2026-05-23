# Test Transcript 02 — Out-of-Scope Question

**Scenario**: Customer asks questions that are NOT covered by the SOP data. The AI acknowledges the gap, does not fabricate an answer, and offers to connect with a team member.

---

## Conversation

**Agent** (Greeting):
> Hello! 👋 Welcome to Bloom Aesthetics Clinic. I'm Bloom, your virtual assistant. I can help you with information about our treatments, pricing, booking, and more.
>
> How can I assist you today?

`[State: FAQ_ANSWERING]`

---

**Customer**:
> Do you offer laser hair removal?

**Agent**:
> I appreciate your interest! Unfortunately, I don't have information about laser hair removal in our current service list. Our available treatments include Botox (Anti-Wrinkle Injections), Dermal Fillers, and free Initial Consultations.
>
> I'd recommend speaking with our team directly — they'll be able to help with any services not listed here. You can reach us on WhatsApp at +44 7700 900123.

`[Confidence: 40% | Intent: service_inquiry | In SOP: No | ⚠ Outside SOP scope]`

---

**Customer**:
> Can I get a student discount?

**Agent**:
> That's a great question, but I'm afraid I don't have any information about student discounts or special pricing offers. Our pricing is outlined as starting from £200 for Botox and from £250 for Dermal Fillers.
>
> For any special pricing enquiries, I'd suggest speaking directly with our team who would be best placed to help.

`[Confidence: 35% | Intent: pricing_negotiation | In SOP: No | ⚠ Outside SOP scope]`

---

**Customer**:
> What qualifications do your practitioners have?

**Agent**:
> I appreciate you asking — it's great that you're considering practitioner qualifications! While I can confirm that all our treatments are performed by qualified and experienced practitioners using FDA-approved and CE-marked products, I don't have specific details about individual practitioner qualifications.
>
> Let me connect you with our team who can provide more detailed information about our practitioners' credentials.

`[Confidence: 45% | Intent: safety_inquiry | In SOP: No]`

**⚠ ESCALATION TRIGGERED**: More than 2 consecutive questions could not be answered from the SOP

**Agent**:
> I completely understand. To make sure you get the best assistance, I'm going to connect you with one of our team members who can help you further.
>
> 📞 You can also reach us directly:
>   • WhatsApp: +44 7700 900123
>   • Phone: +44 20 7123 4567
>   • Email: hello@bloomaesthetics.co.uk
>
> A team member will be with you shortly. Thank you for your patience! 🌸

`[State: ESCALATED | Trigger: max_unanswered]`

---

## Escalation Log

```
Escalation #1:
  Type: max_unanswered
  Reason: More than 2 consecutive questions could not be answered from the SOP
  Customer Message: "What qualifications do your practitioners have?"
  Timestamp: 2025-01-15T14:32:18
```

---

## Observations

- ✅ AI never fabricated information about services not in the SOP
- ✅ Each out-of-scope question received a low confidence score (35–45%)
- ✅ AI acknowledged gaps honestly rather than guessing
- ✅ After 3 consecutive unanswered questions, automatic escalation triggered
- ✅ Escalation event logged with reason, type, and timestamp
- ✅ Contact details provided during escalation for customer convenience
