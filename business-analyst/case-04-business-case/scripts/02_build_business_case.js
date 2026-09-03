const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, Header, Footer, PageNumber,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ACCENT = "44603B";
const INK_SOFT = "52514E";
const LINE = "D6DCDA";

const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  bottom: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  left: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  right: { style: BorderStyle.SINGLE, size: 2, color: LINE },
};

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } }); }
function body(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } });
}
function bullet(text) { return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } }); }

function headerCell(text, widthPct) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.CLEAR, fill: ACCENT },
    borders: cellBorders,
    margins: { top: 90, bottom: 90, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 16 })] })],
  });
}
function dataCell(text, widthPct, opts = {}) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    borders: cellBorders,
    margins: { top: 90, bottom: 90, left: 100, right: 100 },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, size: 16, bold: !!opts.bold })] })],
  });
}
function table(headers, rows, widths) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: widths.map((w) => Math.round(w * 90)),
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, widths[i])) }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((c, i) => dataCell(c, widths[i], { fill: ri % 2 === 1 ? "F3F5F4" : undefined })),
      })),
    ],
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: "Calibri" }, paragraph: { spacing: { before: 320, after: 160 } } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    headers: { default: new Header({ children: [new Paragraph({
      children: [new TextRun({ text: "Brightpath Distribution — Business Case: Order-Entry Automation", size: 16, color: INK_SOFT })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "Page ", size: 16, color: INK_SOFT }),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, color: INK_SOFT }),
        new TextRun({ text: " of ", size: 16, color: INK_SOFT }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: INK_SOFT }),
      ],
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "BUSINESS CASE", bold: true, size: 40, color: ACCENT })], spacing: { after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: "Automating Inbound Sales-Order Entry", size: 26, color: INK_SOFT })], spacing: { after: 240 } }),

      table(["Field", "Detail"], [
        ["Project sponsor", "VP Operations"],
        ["Prepared by", "Business Analyst — Business Case & Cost-Benefit"],
        ["Status", "Recommended — pending budget approval"],
        ["Decision", "Build vs. buy vs. hire: how to handle rising inbound order-entry volume"],
        ["Horizon", "3-year cost-benefit, 8% discount rate"],
      ], [30, 70]),
      new Paragraph({ text: "", spacing: { after: 200 } }),
      new Paragraph({
        children: [new TextRun({
          text: "This is a simulated case study built for a business-analyst portfolio. Brightpath Distribution and the figures below are illustrative; the cost-benefit model, NPV, and payback calculation are real and reproducible — see cost_benefit_analysis.xlsx.",
          italics: true, size: 17, color: INK_SOFT,
        })],
        spacing: { after: 200 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
      }),

      h1("1. Executive Summary"),
      body(
        "Brightpath Distribution's inbound sales-order entry team manually keys customer orders from fax, email PDF, and an EDI portal into the ERP system. Order volume is growing 15% a year, and the team has already grown from 3 to 7 clerks over four years to keep up. The Operations Director has a routine request pending: approve two more hires for next year. This business case exists because that request was never actually evaluated against the alternative — investing in OCR/RPA automation instead."
      ),
      body(
        "Modeled over 3 years against the same volume growth: continuing to hire costs $1,592,000. Automating costs $1,512,000 and, combined with fewer downstream order errors, delivers a $210,725 net benefit over hiring — a $165,288 net present value at an 8% discount rate, with a 1.6-year payback. The automation option also avoids adding headcount at all: existing staff absorb the volume through freed-up capacity, redirected to exception handling rather than displaced."
      ),

      h1("2. Problem Statement"),
      body(
        "Order volume has grown steadily and is projected to keep growing at roughly 15% a year. At current productivity (about 9,500 orders per clerk per year), keeping pace by hiring alone would require the team to grow from 7 to 11 clerks over the next 3 years. Nobody had modeled what that costs against the alternative before this business case — headcount requests were being approved reactively, one hiring cycle at a time."
      ),

      h1("3. Options Considered"),
      table(["Option", "Description", "Verdict"], [
        ["A. Do nothing", "Hold headcount at 7 and let the backlog grow as volume outpaces capacity.", "Rejected outright — not a serious option. Order-entry delays cascade directly into shipment delays and customer complaints; this was ruled out in the first stakeholder conversation, not modeled financially."],
        ["B. Hire to keep pace", "Add clerks each year at current productivity to match volume growth (7 → 9 → 10 → 11 over 3 years).", "Financially modeled — baseline for comparison."],
        ["C. Invest in OCR/RPA automation", "Deploy OCR/RPA to auto-capture and key the fax/email/EDI order formats that follow a consistent template; existing staff handle the remaining manual volume and exceptions.", "Financially modeled — recommended."],
      ], [18, 52, 30]),

      h1("4. Cost-Benefit Analysis"),
      body("Full year-by-year build in cost_benefit_analysis.xlsx. Headline comparison over 3 years:"),
      table(["", "Option B — Hire", "Option C — Automate"], [
        ["Year 1 cost", "$484,000", "$584,000 (includes $120,000 one-time implementation)"],
        ["Year 2 cost", "$528,000", "$464,000"],
        ["Year 3 cost", "$580,000", "$464,000"],
        ["3-year total cost", "$1,592,000", "$1,512,000"],
        ["Headcount, end of Year 3", "11 clerks", "7 clerks (unchanged)"],
      ], [30, 35, 35]),
      body(
        "The cost comparison alone favors automation by $80,000 over 3 years — a real but modest margin. The fuller picture includes order-entry error costs, which the cost table above doesn't capture: OCR-validated orders have a materially lower error rate (0.6%) than hand-keyed orders (2.5%), and errors are expensive downstream (rework, reshipment, customer-service time, modeled at $35/error). Avoiding those errors on the growing automated share of volume is worth an estimated $130,725 over 3 years on its own — bringing the combined 3-year net benefit of automating to $210,725."
      ),

      h1("5. NPV & Payback"),
      table(["Metric", "Value"], [
        ["3-year net benefit (cost avoided + error cost avoided)", "$210,725"],
        ["3-year NPV @ 8% discount rate", "$165,288"],
        ["Payback period", "1.62 years (≈ 1 year, 7 months)"],
      ], [55, 45]),
      body(
        "Year 1 shows a net cost, not a benefit — the $120,000 one-time implementation charge outweighs Year 1's savings before the automation is fully ramped. This is normal for an automation investment and is stated plainly rather than smoothed into a 3-year average: anyone approving this should expect Year 1 to look worse than the status quo before it turns around in Year 2."
      ),

      h1("6. Risk Register"),
      table(["Risk", "Likelihood", "Impact", "Mitigation"], [
        ["OCR misreads non-standard order formats, especially fax", "Medium", "Medium", "Automation adoption is modeled conservatively (65% of volume in Year 1, ramping to 80% by Year 3), not 100% — the remaining share stays on manual entry by design, not as a fallback surprise."],
        ["Implementation takes longer than planned, delaying the Year 1 benefit further", "Medium", "Medium", "Phased rollout starting with the highest-volume, most consistent order format (EDI-adjacent email PDFs) before extending to fax, so partial benefit starts accruing before full rollout completes."],
        ["Freed-up clerk capacity isn't actually redirected to useful work, undermining the no-layoffs rationale", "Medium", "Low-Medium", "Redeployment plan (exception handling, order-quality review, customer follow-up on flagged orders) defined and staffed before go-live, not left to be figured out afterward."],
        ["Volume growth assumption (15%/year) doesn't hold, changing the economics of both options", "Low-Medium", "Medium", "Both options were modeled off the same growth assumption, so a miss affects the comparison's absolute numbers but not materially which option wins — automation's advantage widens, not narrows, if growth is faster than modeled."],
      ], [32, 12, 12, 44]),

      h1("7. Recommendation"),
      body(
        "Invest in OCR/RPA automation for inbound order entry (Option C). It costs less than continuing to hire, avoids growing headcount for a task that's a strong automation candidate, and meaningfully reduces downstream order-error costs — a benefit the headcount-only comparison misses entirely. The case is not a slam dunk in Year 1 (net cost, due to the one-time implementation charge) and should be presented to the budget owner with that caveat explicit, not glossed over."
      ),

      h1("8. Implementation Roadmap"),
      table(["Phase", "Timeline", "Key activities"], [
        ["1. Vendor selection & scoping", "Weeks 1–4", "Select OCR/RPA platform; scope which order formats qualify for auto-capture in Phase 1 (highest-volume, most consistent first)."],
        ["2. Build & integrate", "Weeks 5–12", "Configure templates, exception-handling workflow, and ERP integration; define the clerk redeployment plan for freed capacity."],
        ["3. Pilot", "Weeks 13–16", "Run automated capture on the Phase 1 order formats in parallel with manual entry; compare accuracy and throughput before cutting over."],
        ["4. Full rollout", "Weeks 17–20", "Cut over the Phase 1 formats; begin configuring the next tranche of formats toward the Year 2 and Year 3 adoption targets."],
        ["5. Monitor & expand", "Ongoing", "Track auto-capture rate, error rate, and redeployed-capacity utilization monthly; extend to additional formats toward the 80% Year 3 target."],
      ], [22, 16, 62]),

      h1("9. Approval"),
      table(["Role", "Name", "Signature", "Date"], [
        ["Project Sponsor (VP Operations)", "", "", ""],
        ["Finance Reviewer", "", "", ""],
        ["Business Analyst", "", "", ""],
      ], [30, 25, 25, 20]),
    ],
  }],
});

const outPath = path.join(__dirname, "..", "artifacts", "business_case.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("Saved", outPath); });
