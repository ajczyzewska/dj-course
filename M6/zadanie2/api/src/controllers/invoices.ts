import { Request, Response } from "express";
import { fetchAllInvoices, createNewInvoice } from "../services/invoiceService";
import { getCache, setCache, invalidateCache } from "../db/redis";

const CACHE_KEY = "invoices:list";
const CACHE_TTL = 30;

export async function getInvoices(_req: Request, res: Response) {
  try {
    const cached = await getCache(CACHE_KEY);
    if (cached) {
      console.log("Cache HIT");
      return res.json(cached);
    }

    console.log("Cache MISS");
    const invoices = await fetchAllInvoices();
    await setCache(CACHE_KEY, invoices, CACHE_TTL);
    return res.json(invoices);
  } catch (err) {
    console.error("GET /invoices error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
}

export async function postInvoice(req: Request, res: Response) {
  try {
    const { number, amount, customer } = req.body;

    if (!number || amount == null || !customer) {
      return res.status(400).json({ error: "Fields number, amount, customer are required" });
    }

    const invoice = await createNewInvoice({ number, amount, customer });
    await invalidateCache(CACHE_KEY);

    return res.status(201).json(invoice);
  } catch (err) {
    console.error("POST /invoices error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
}
