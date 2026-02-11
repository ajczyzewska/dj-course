import { Router } from "express";
import { getInvoices, postInvoice } from "../controllers/invoices";

const router = Router();

router.get("/", getInvoices);
router.post("/", postInvoice);

export default router;
