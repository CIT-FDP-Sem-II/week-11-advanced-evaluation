# AI Decision Journal — Entry (Week 11)

**Question:** What did the regression test tell you that the accuracy number
did not?

Half a page.

---

## 1. The delta

```
(paste the REGRESSION REPORT output)
```

## 2. What the change was meant to do

> One sentence. From `src/prompts.py` — the intent is written next to the
> prompt.

## 3. What it actually did

| | Count | Cases |
|---|------:|-------|
| Fixed | | |
| **Broken** | | |
| Unchanged | | |

## 4. The trade

> For each broken case: is losing it worth the thing you fixed?
>
> This is a judgement, not a calculation. Make it explicitly and write down
> who would disagree.

## 5. Would you ship it?

> Yes or no, and the one condition that would change your answer.

## 6. The one that surprised you

> Which case flipped that you did not predict? Why do you think it did?
>
> If nothing surprised you, either your dataset is too small or your change
> was too timid. Say which.

---

### What to notice

The point of this week is that **an overall accuracy number is not a
regression test**. A prompt change can leave the total untouched and still
flip a third of your cases — some into passing, some out.

If your totals were identical and cases still moved, the harness prints a
line saying so. Quote it.
