# Test Transcript 04 — Lead Qualification

**Scenario**: Customer asks several FAQ questions. After 3 FAQ turns, the agent transitions to lead qualification, asks 3 structured questions, collects the answers, and produces a qualification summary.

---

## Conversation

**Agent** (Greeting):
> Hello! 👋 Welcome to Bloom Aesthetics Clinic. I'm Bloom, your virtual assistant. I can help you with information about our treatments, pricing, booking, and more.
>
> How can I assist you today?

`[State: FAQ_ANSWERING]`

---

**Customer**:
> Hi! What services do you offer?

**Agent**:
> Welcome! We currently offer three services:
>
> 1. **Botox (Anti-Wrinkle Injections)** — starting from £200, takes 20–30 minutes
> 2. **Dermal Fillers** — starting from £250, takes 30–45 minutes
> 3. **Initial Consultation** — completely free, 15–20 minutes
>
> Would you like to know more about any of these?

`[Confidence: 95% | Intent: service_inquiry | In SOP: Yes]`

---

**Customer**:
> How do I book an appointment?

**Agent**:
> Booking is easy! You have two options:
>
> 📱 **WhatsApp**: Send us a message at +44 7700 900123
> 💻 **Website**: Book online at www.bloomaesthetics.co.uk/book
>
> Please note that a £50 deposit is required to secure your booking, which is deducted from your treatment cost. We also ask for at least 24 hours' notice for cancellations.

`[Confidence: 95% | Intent: booking_request | In SOP: Yes]`

---

**Customer**:
> Do I need a consultation first?

**Agent**:
> We offer a free initial consultation where we assess your needs and create a personalised treatment plan. While it's not mandatory for all treatments, we highly recommend it — especially if it's your first time. The consultation is 15–20 minutes with no obligation to proceed. 🌸
>
> I'd love to learn a little more about you so we can tailor our recommendations. May I ask a few quick questions?
>
> What type of treatment are you most interested in?

`[Confidence: 95% | Intent: consultation_inquiry | In SOP: Yes]`
`[State: QUALIFYING — Lead qualification started after 3 FAQ turns]`

---

**Customer**:
> I'm mainly interested in lip fillers

**Agent**:
> Lovely choice! Lip fillers are one of our most popular treatments. Thank you for sharing that.
>
> Is this your first time considering aesthetic treatments, or have you had similar treatments before?

`[State: QUALIFYING — Question 2 of 3]`

---

**Customer**:
> This would be my first time actually. A bit nervous!

**Agent**:
> That's completely understandable — many of our clients feel the same way before their first treatment! Our practitioners are very experienced and will make sure you feel comfortable throughout.
>
> How did you hear about Bloom Aesthetics Clinic?

`[State: QUALIFYING — Question 3 of 3]`

---

**Customer**:
> My friend recommended you, she had fillers here last year

**Agent**:
> That's wonderful — word of mouth is the best recommendation! Thank you so much for sharing that. Here's what I've noted:
>
> • **What type of treatment are you most interested in?**
>   → I'm mainly interested in lip fillers
>
> • **Is this your first time considering aesthetic treatments, or have you had similar treatments before?**
>   → This would be my first time actually. A bit nervous!
>
> • **How did you hear about Bloom Aesthetics Clinic?**
>   → My friend recommended you, she had fillers here last year
>
> I'll make sure this information is available for your practitioner. Would you like to book a free consultation, or is there anything else I can help with? 🌸

`[State: FAQ_ANSWERING — Qualification complete, returning to FAQ]`

---

## Qualification Summary

| Question | Response |
|----------|----------|
| Treatment interest | Lip fillers |
| Prior experience | First time — expressed nervousness |
| Acquisition channel | Friend recommendation (word of mouth) |

**Lead Status**: Qualified — clear intent, first-time customer, warm referral

---

## Observations

- ✅ Natural transition from FAQ answering to qualification after 3 turns
- ✅ Qualification intro is conversational, not robotic
- ✅ All 3 questions asked sequentially, one at a time
- ✅ Agent acknowledges each answer warmly before asking the next question
- ✅ Reassured the nervous first-time customer (empathetic response)
- ✅ Clean qualification summary produced with all responses
- ✅ After qualification, agent returns to FAQ state for further questions
