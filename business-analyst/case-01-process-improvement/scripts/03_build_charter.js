const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, PageOrientation, Header, Footer,
  PageNumber, NumberFormat, LevelFormat, convertInchesToTwip
} = require("docx");
const fs = require("fs");
const path = require("path");

const ACCENT = "44603B";
const ACCENT_WASH = "E4EBE1";
const INK_SOFT = "52514E";
const LINE = "D6DCDA";

const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  bottom: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  left: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  right: { style: BorderStyle.SINGLE, size: 2, color: LINE },
};

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });
}
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 160 },
  });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}

function headerCell(text, widthPct) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.CLEAR, fill: ACCENT },
    borders: cellBorders,
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 18 })] })],
  });
}
function dataCell(text, widthPct, opts = {}) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    borders: cellBorders,
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, size: 18, bold: !!opts.bold })] })],
  });
}

function table(headers, rows, widths) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: widths.map((w) => Math.round(w * 90)),
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, widths[i])) }),
      ...rows.map(
        (r, ri) =>
          new TableRow({
            children: r.map((c, i) => dataCell(c, widths[i], { fill: ri % 2 === 1 ? "F3F5F4" : undefined })),
          })
      ),
    ],
  });
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 20 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: "Calibri" },
        paragraph: { spacing: { before: 320, after: 160 } },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, color: "2A2A2A", font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 120 } },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              children: [new TextRun({ text: "Brightpath Distribution — Process Improvement Charter", size: 16, color: INK_SOFT })],
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "Page ", size: 16, color: INK_SOFT }),
                new TextRun({ children: [PageNumber.CURRENT], size: 16, color: INK_SOFT }),
                new TextRun({ text: " of ", size: 16, color: INK_SOFT }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: INK_SOFT }),
              ],
            }),
          ],
        }),
      },
      children: [
        new Paragraph({
          children: [new TextRun({ text: "PROCESS IMPROVEMENT CHARTER", bold: true, size: 40, color: ACCENT })],
          spacing: { after: 80 },
        }),
        new Paragraph({
          children: [new TextRun({ text: "AP Invoice Approval Cycle Time", size: 26, color: INK_SOFT })],
          spacing: { after: 240 },
        }),

        table(
          ["Field", "Detail"],
          [
            ["Project sponsor", "VP Finance"],
            ["Process owner", "Accounts Payable Manager"],
            ["Prepared by", "Business Analyst — Process Improvement"],
            ["Status", "Recommended — pending sponsor sign-off"],
            ["Scope", "Accounts Payable invoice approval workflow, all departments"],
          ],
          [30, 70]
        ),
        new Paragraph({ text: "", spacing: { after: 200 } }),
        new Paragraph({
          children: [
            new TextRun({
              text:
                "This is a simulated case study built for a business-analyst portfolio. Brightpath Distribution, its people, and the figures below are illustrative; the discovery method, the analysis, and the workbook behind it are real and reproducible — see cycle_time_analysis.xlsx.",
              italics: true, size: 17, color: INK_SOFT,
            }),
          ],
          spacing: { after: 200 },
          border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        }),

        h1("1. Executive Summary"),
        body(
          "Brightpath Distribution's accounts-payable invoice approval process takes an average of 12.8 business days from invoice receipt to payment, against vendor terms that reward payment inside 10 days. A one-month sample of 120 invoices, pulled from AP timestamps and approver email logs, shows the delay is structural, not occasional: every invoice of $500 or more is routed through the same three sequential approvals — department manager, finance manager, and controller — regardless of whether it is a $600 office-supply order or a $60,000 equipment purchase."
        ),
        body(
          "The direct cost is measurable: this sample alone forfeited $10,401 in early-payment discounts in one month, an estimated $124,815 annualized. Nothing in the process is unfixable — the fix is to differentiate approval requirements by dollar amount, remove manual data entry for recurring vendors, and replace untracked email routing with a workflow tool that has visibility and backup approvers. Modeled against this same invoice population, that redesign cuts average cycle time to 4.3 days (a 66% reduction) and is projected to net roughly $75,000 in year one and $97,000 in every year after, against a combined tool and implementation cost of $49,600."
        ),

        h1("2. Problem Statement"),
        body(
          "Finance leadership raised two recurring complaints: vendors increasingly declining to offer early-payment discount terms to Brightpath, citing unreliable payment timing, and AP staff spending a disproportionate amount of time chasing approvals rather than processing invoices. Neither complaint pointed to a specific cause, only a feeling that “invoices take too long.” This charter exists to answer, with data, where the time actually goes and what a fix is worth."
        ),

        h1("3. Current-State Process"),
        body(
          "See the companion exhibit, process-map.html, for the full swimlane diagram. In summary: every invoice is manually re-keyed from PDF into the accounting system by an AP clerk (avg. 1.3 days), then routed by individual email to a department manager (avg. 4.2 days), a finance manager (avg. 3.6 days), and a controller (avg. 4.2 days) in sequence — for any invoice at or above $500, with no exceptions for size. No backup approver is defined for any of the three roles, so a single approver's absence stalls the invoice until they return. Approval status is not tracked anywhere outside individual inboxes."
        ),

        h1("4. Root-Cause Analysis"),
        body("Structured as 5 Whys, starting from the symptom finance raised:"),
        table(
          ["Why", "Finding"],
          [
            ["1. Why do invoices take ~13 days to pay?", "They pass through 3 sequential manual approvals plus manual data entry before payment is scheduled."],
            ["2. Why 3 approvals for every invoice?", "The approval policy was never updated after the company's headcount and invoice volume grew; it was written when total monthly invoice volume was roughly a third of today's."],
            ["3. Why does each approval take 3–4 days?", "Requests are single email threads with no reminders, no visibility, and no deadline. An approver has to notice, open, and act on each one individually."],
            ["4. Why is there no reminder or visibility system?", "AP has never had a workflow tool; the process was built for a much smaller, lower-volume operation and grew by habit rather than design."],
            ["5. Why does data entry take over a day?", "Every invoice, including the ~75% from recurring, known vendors with a consistent format, is keyed in by hand rather than captured automatically."],
          ],
          [42, 58]
        ),
        new Paragraph({ text: "", spacing: { after: 120 } }),
        body(
          "Root cause: the approval policy and the tooling around it were designed for a smaller company and never revisited as volume grew. The fix is not “work faster” — it is redesigning the policy to match risk to invoice size, and giving approvers a tool that surfaces work instead of burying it in email."
        ),

        h1("5. Future-State Recommendation"),
        body("Three changes, implemented together:"),
        bullet("Tier approvals by invoice amount: under $500 stays department-manager-only (unchanged); $500–$10,000 drops to department-manager-only; $10,000–$50,000 requires department + finance manager; above $50,000 keeps the full three-approval chain."),
        bullet("Deploy OCR/auto-capture for the ~75% of invoice volume from established, recurring vendors, eliminating manual re-keying for that population."),
        bullet("Replace email routing with a lightweight approval workflow tool: automatic reminders, a defined backup approver for each role, and a shared queue so AP can see where any invoice actually sits."),
        body(
          "Modeled row-by-row against the same 120-invoice sample (see the Future-State Model and Future-State Projection tabs in cycle_time_analysis.xlsx), this reduces average cycle time from 12.8 to 4.3 days — a 66% reduction — and is projected to recover $124,815/year in early-payment discounts that are currently forfeited."
        ),

        h1("6. Success Metrics"),
        table(
          ["Metric", "Current", "Target (Month 6)"],
          [
            ["Average invoice cycle time (receipt to payment)", "12.8 days", "≤ 5.0 days"],
            ["% of eligible invoices capturing early-payment discount", "22%", "≥ 80%"],
            ["Invoices routed through all 3 approval tiers", "82% (all $500+ invoices)", "≈ 7% (only Tier 3, >$50K)"],
            ["Invoices with no defined backup approver", "100%", "0%"],
          ],
          [46, 27, 27]
        ),

        h1("7. Implementation Plan"),
        table(
          ["Phase", "Timeline", "Key activities"],
          [
            ["1. Policy redesign & sign-off", "Weeks 1–2", "Finalize tier thresholds with Finance leadership; update the AP approval policy document; identify and confirm backup approvers for each role."],
            ["2. Tool selection & configuration", "Weeks 3–6", "Select and configure workflow/routing tool and OCR capture tool; integrate with the existing accounting system; build the tiered routing rules."],
            ["3. Pilot", "Weeks 7–8", "Run the new process for one department's invoices in parallel with the old process; compare cycle times; fix routing-rule edge cases."],
            ["4. Company-wide rollout & training", "Weeks 9–10", "Roll out to all departments; train approvers and AP staff; publish the updated policy and escalation path."],
            ["5. Monitor & adjust", "Weeks 11–16", "Track the Section 6 metrics monthly; revisit tier thresholds if volume in any tier looks miscalibrated."],
          ],
          [26, 16, 58]
        ),

        h1("8. Risks & Mitigations"),
        table(
          ["Risk", "Mitigation"],
          [
            ["OCR misreads non-standard invoice formats from one-off vendors", "Auto-capture is scoped only to the ~75% of volume from recurring, known-format vendors; one-off vendors keep manual entry, flagged as a known limitation rather than forced through OCR."],
            ["Approvers don't adopt the new tool and keep using email", "Old routing is disabled, not left as a parallel option; training in Phase 4 is mandatory and tied to the policy update, not optional."],
            ["Raising a department manager's authority to single-approve up to $10,000 increases risk exposure", "Threshold was set with Finance leadership using Brightpath's existing delegation-of-authority policy, not chosen unilaterally by this project; spot-audits of Tier 1 approvals continue for the first two quarters."],
            ["Benefit estimate depends on assumptions (queue-time reduction %, OCR adoption) that may not hold exactly", "All assumptions are isolated in the Future-State Model tab as labeled, editable cells — the pilot in Phase 3 will validate them against real data before company-wide rollout."],
          ],
          [40, 60]
        ),

        h1("9. Approval"),
        table(
          ["Role", "Name", "Signature", "Date"],
          [
            ["Project Sponsor (VP Finance)", "", "", ""],
            ["Process Owner (AP Manager)", "", "", ""],
            ["Business Analyst", "", "", ""],
          ],
          [30, 25, 25, 20]
        ),
      ],
    },
  ],
});

const outPath = path.join(__dirname, "..", "artifacts", "process_improvement_charter.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log("Saved", outPath);
});
