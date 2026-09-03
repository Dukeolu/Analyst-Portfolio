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
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
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
    children: [new Paragraph({ children: [new TextRun({ text, size: 16, bold: !!opts.bold, color: opts.color })] })],
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
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 21, bold: true, color: "2A2A2A", font: "Calibri" }, paragraph: { spacing: { before: 220, after: 110 } } },
    ],
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } },
    },
    headers: { default: new Header({ children: [new Paragraph({
      children: [new TextRun({ text: "Brightpath Distribution — CRM Business Requirements Document", size: 16, color: INK_SOFT })],
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
      new Paragraph({ children: [new TextRun({ text: "BUSINESS REQUIREMENTS DOCUMENT", bold: true, size: 40, color: ACCENT })], spacing: { after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: "Sales CRM Replacement", size: 26, color: INK_SOFT })], spacing: { after: 240 } }),

      table(["Field", "Detail"], [
        ["Project sponsor", "VP Sales"],
        ["Requirements owner", "Sales Operations Manager"],
        ["Prepared by", "Business Analyst — Requirements & Systems Selection"],
        ["Status", "Approved — vendor recommendation attached"],
        ["Scope", "Sales team CRM (pipeline, forecasting, mobile, integration) — 40 seats"],
      ], [30, 70]),
      new Paragraph({ text: "", spacing: { after: 200 } }),
      new Paragraph({
        children: [new TextRun({
          text: "This is a simulated case study built for a business-analyst portfolio. Brightpath Distribution, its people, and the stakeholder quotes below are illustrative; the requirements-gathering method and the vendor scoring model are real and reproducible — see vendor_evaluation_matrix.xlsx.",
          italics: true, size: 17, color: INK_SOFT,
        })],
        spacing: { after: 200 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
      }),

      h1("1. Purpose"),
      body("Brightpath Distribution's 40-person sales team is running on a 9-year-old on-premise CRM that most reps have stopped using, supplemented by personal spreadsheets and email. This document captures the business requirements gathered from sales, sales operations, IT, finance, and marketing stakeholders for a replacement system, and traces those requirements through to a vendor recommendation."),

      h1("2. Business Objectives"),
      table(["ID", "Objective"], [
        ["BO-1", "Give sales leadership a real-time, accurate view of pipeline and forecast, without manual spreadsheet consolidation."],
        ["BO-2", "Reduce the time reps spend on administrative data entry so more of the day goes to selling."],
        ["BO-3", "Connect sales data with ERP order history and marketing-qualified leads, eliminating manual handoffs between systems."],
        ["BO-4", "Support field selling with reliable, usable mobile access."],
      ], [15, 85]),

      h1("3. Current-State Pain Points"),
      body("Drawn from structured interviews with 6 sales reps across 3 regions, 4 regional sales managers, the VP Sales, the IT Director, a Finance/RevOps analyst, and the Marketing Ops manager (13 interviews total):"),
      bullet("5 of 6 reps interviewed keep a personal pipeline spreadsheet because the current CRM is slow and not usable from the field — meaning the official system is not the actual source of truth for a majority of the team."),
      bullet("The weekly forecast deck is manually rebuilt from four separate regional spreadsheets; it is routinely 2+ weeks out of date by the time it reaches the VP Sales."),
      bullet("Reps have no visibility into a customer's order history without asking Finance directly, since the CRM has no connection to the ERP system."),
      bullet("Marketing-qualified leads are forwarded to reps by email and, per the Marketing Ops manager, a meaningful share go unactioned for several days or longer."),
      bullet("There is no mobile access; field notes are taken on paper or in personal note-taking apps and often never make it back into any system."),

      h1("4. Stakeholders"),
      table(["Stakeholder", "Role in this project"], [
        ["VP Sales", "Executive sponsor; final approval on recommendation"],
        ["Sales Operations Manager", "Requirements owner; day-to-day project lead"],
        ["Regional Sales Managers (4)", "Pipeline and reporting requirements"],
        ["Sales Reps (6, sampled across regions)", "Day-to-day usability and mobile requirements"],
        ["IT Director", "Integration, security, and hosting requirements"],
        ["Finance / RevOps Analyst", "Forecasting and reporting requirements"],
        ["Marketing Operations Manager", "Lead-handoff and integration requirements"],
      ], [40, 60]),

      h1("5. Scope"),
      body("In scope: pipeline and opportunity management, forecasting and reporting, mobile access, integration with company email/calendar, the ERP system, and the marketing automation platform, and data migration from the legacy CRM and sales spreadsheets for all 40 seats."),
      body("Out of scope: a customer support/ticketing system, a quote/CPQ configurator (deferred to a future phase — see FR-14), and a partner/reseller portal."),

      h1("6. Functional Requirements"),
      body("Prioritized using MoSCoW (Must / Should / Could / Won't-this-phase), based on interview frequency and business-objective impact."),
      table(["ID", "Requirement", "Priority", "Source"], [
        ["FR-01", "Track opportunities through configurable pipeline stages", "Must", "Sales Ops"],
        ["FR-02", "Real-time, shared pipeline value view by rep, team, and region", "Must", "VP Sales, Regional Mgrs"],
        ["FR-03", "Log an activity against an opportunity in under 30 seconds", "Should", "Sales Reps"],
        ["FR-04", "Generate a rolling forecast without manual spreadsheet consolidation", "Must", "Finance/RevOps"],
        ["FR-05", "Drill from a regional forecast down to individual opportunities", "Must", "VP Sales"],
        ["FR-06", "Custom report builder for ad hoc Finance requests", "Should", "Finance/RevOps"],
        ["FR-07", "Native mobile app, usable offline for field visits", "Must", "Sales Reps"],
        ["FR-08", "Update opportunity status from the mobile app in one screen", "Should", "Sales Reps"],
        ["FR-09", "Integrate with company email/calendar; auto-sync activities", "Must", "IT Director"],
        ["FR-10", "Integrate with the ERP system for order history on customer records", "Must", "IT Director, Sales Reps"],
        ["FR-11", "Integrate with the marketing automation tool to pass qualified leads", "Should", "Marketing Ops"],
        ["FR-12", "Integrate with an e-signature tool for quote approval", "Could", "Sales Ops"],
        ["FR-13", "Import existing customer and opportunity data without data loss", "Must", "Sales Ops, IT"],
        ["FR-14", "Custom quote/CPQ configurator", "Won't (this phase)", "Sales Ops"],
      ], [10, 52, 18, 20]),

      h1("7. Non-Functional Requirements"),
      table(["ID", "Requirement"], [
        ["NFR-01", "99.5% uptime SLA during business hours"],
        ["NFR-02", "Role-based access control — reps see only their own accounts and opportunities unless in a manager role"],
        ["NFR-03", "Data encrypted at rest and in transit; vendor must hold current SOC 2 Type II certification"],
        ["NFR-04", "Pipeline dashboard loads in under 2 seconds on standard company wifi"],
        ["NFR-05", "Mobile app supports the two most recent major iOS and Android releases"],
      ], [15, 85]),

      h1("8. Requirements Traceability Matrix"),
      body("Each requirement traced to the business objective it serves and checked against the recommended vendor (Northstar CRM — see the Vendor Evaluation Matrix, Section 9) based on the evaluation panel's product demos."),
      table(["ID", "Objective", "Priority", "Northstar CRM"], [
        ["FR-01", "BO-1", "Must", "Yes"],
        ["FR-02", "BO-1", "Must", "Yes"],
        ["FR-03", "BO-2", "Should", "Yes"],
        ["FR-04", "BO-1", "Must", "Yes"],
        ["FR-05", "BO-1", "Must", "Yes"],
        ["FR-06", "BO-1", "Should", "Partial — built-in report builder is more limited than the closest competitor's"],
        ["FR-07", "BO-4", "Must", "Yes"],
        ["FR-08", "BO-4", "Should", "Yes"],
        ["FR-09", "BO-3", "Must", "Yes"],
        ["FR-10", "BO-3", "Must", "Partial — requires a middleware connector, not a native integration"],
        ["FR-11", "BO-3", "Should", "Partial — supported via connector, not native"],
        ["FR-12", "BO-3", "Could", "No — would need a third-party e-signature add-on"],
        ["FR-13", "BO-2", "Must", "Yes"],
      ], [10, 14, 14, 62]),

      h1("9. Vendor Recommendation"),
      body("Three vendors were evaluated against these requirements, weighted by business-objective priority, in a formal scoring model (see vendor_evaluation_matrix.xlsx and the vendor-scorecard.html exhibit). Northstar CRM scored highest (4.22 of 5, weighted) against Vertex Sales Suite (4.01) and Pinnacle Sales Cloud (3.57), and carries the lowest 3-year total cost of ownership of the three ($206,560 for 40 seats)."),
      body("Northstar's clearest gap is integration (FR-10, FR-11): both the ERP and marketing-automation connections require middleware rather than a native integration. This should be scoped and quoted as part of implementation planning, not discovered during rollout — it is the one area where the runner-up, Vertex Sales Suite, is genuinely stronger, and was the deciding factor debated longest by the evaluation panel before Northstar's pipeline, mobile, and cost advantages carried the recommendation."),

      h1("10. Assumptions & Constraints"),
      bullet("Finance set a 3-year budget ceiling of $250,000 for the replacement CRM prior to vendor evaluation; all three shortlisted vendors were pre-screened to fit within it."),
      bullet("Migration must be scheduled outside Brightpath's fiscal year-end close (November–December) to avoid disrupting quarter-end reporting."),
      bullet("All 40 seats migrate simultaneously; a phased-by-region rollout was considered and rejected by the VP Sales due to the added complexity of consolidating a forecast across two systems mid-transition."),
      bullet("IT will not support on-premise hosting for this system; cloud/SaaS delivery only."),

      h1("Appendix — Interview Participants"),
      body("VP Sales; Sales Operations Manager; 4 Regional Sales Managers (North, South, East, West); 6 Sales Reps (2 per region, mixed tenure); IT Director; Finance/RevOps Analyst; Marketing Operations Manager. Interviews conducted individually, 30–45 minutes each, over a two-week discovery period."),
    ],
  }],
});

const outPath = path.join(__dirname, "..", "artifacts", "business_requirements_document.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("Saved", outPath); });
