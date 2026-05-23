# Test Transcript 03 — Escalation Trigger (Frustrated Customer)

**Scenario**: Customer expresses frustration and makes a complaint. The AI detects angry sentiment and hands off to a human agent with an empathetic response. The escalation is logged with the reason.

---

## Conversation

**Agent** (Greeting):
> Hello! 👋 Welcome to Bloom Aesthetics Clinic. I'm Bloom, your virtual assistant. I can help you with information about our treatments, pricing, booking, and more.
>
> How can I assist you today?

`[State: FAQ_ANSWERING]`

---

**Customer**:
> Hi, I want to know about your Botox treatment

**Agent**:
> Hello! I'd be happy to tell you about our Botox treatments. 🌸
>
> Our Botox (Anti-Wrinkle Injections) start from £200. The treatment takes around 20–30 minutes, and you'll start seeing results within 3–5 days, with the full effect visible in about 2 weeks. Results typically last 3–4 months.
>
> Treatment areas include forehead lines, frown lines, and crow's feet. Would you like to book a free consultation to discuss your options?

`[Confidence: 95% | Intent: service_inquiry | In SOP: Yes]`

---

**Customer**:
> Actually, I had Botox done at your clinic last month and I'm really unhappy. The results were terrible and uneven. I've been trying to call but nobody picks up. This is absolutely awful service!

**Agent**:
> I'm truly sorry to hear about your experience — that sounds really frustrating, and I completely understand your concern. Your satisfaction is incredibly important to us, and I want to make sure this is addressed properly.
>
> This is something that needs to be handled by our clinical team directly, so I'm going to connect you with a team member who can review your case and help resolve this for you.

**⚠ ESCALATION TRIGGERED**: Customer complaint with angry sentiment detected

**Agent**:
> I completely understand. To make sure you get the best assistance, I'm going to connect you with one of our team members who can help you further.
>
> 📞 You can also reach us directly:
>   • WhatsApp: +44 7700 900123
>   • Phone: +44 20 7123 4567
>   • Email: hello@bloomaesthetics.co.uk
>
> A team member will be with you shortly. Thank you for your patience! 🌸

`[State: ESCALATED | Trigger: complaint + angry_sentiment]`

---

**Customer**:
> How long will I have to wait?

**Agent**:
> Our team has been notified and will be with you shortly. In the meantime, you can reach us at +44 7700 900123 on WhatsApp. Thank you for your patience! 🌸

`[State: ESCALATED — all subsequent messages receive the handoff response]`

---

## Escalation Log

```
Escalation #1:
  Type: complaint
  Reason: Customer expressed dissatisfaction with treatment results and described a negative experience. Angry sentiment detected.
  Customer Message: "Actually, I had Botox done at your clinic last month and I'm really unhappy. The results were terrible and uneven. I've been trying to call but nobody picks up. This is absolutely awful service!"
  Timestamp: 2025-01-15T10:15:42
```

---

## Observations

- ✅ Agent detected complaint + angry sentiment immediately
- ✅ Empathetic acknowledgment before escalation — did not dismiss the concern
- ✅ Did NOT attempt to resolve the medical complaint itself
- ✅ Provided clear next steps and contact details
- ✅ After escalation, all subsequent messages receive the handoff message
- ✅ Escalation event logged with full reason and customer message
