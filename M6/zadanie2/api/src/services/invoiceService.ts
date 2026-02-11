import { Invoice } from "../db/mongo";
import { IInvoice } from "../types";

export async function fetchAllInvoices() {
  return Invoice.find().lean();
}

export async function createNewInvoice(data: IInvoice) {
  const invoice = new Invoice(data);
  return invoice.save();
}
