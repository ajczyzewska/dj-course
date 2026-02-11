import mongoose, { Schema } from "mongoose";
import { IInvoice } from "../types";

const invoiceSchema = new Schema<IInvoice>({
  number: { type: String, required: true },
  amount: { type: Number, required: true },
  customer: { type: String, required: true },
});

export const Invoice = mongoose.model<IInvoice>("Invoice", invoiceSchema);

export async function connectMongo(): Promise<void> {
  const uri = process.env.MONGO_URI!;
  const maxRetries = 5;

  for (let i = 0; i < maxRetries; i++) {
    try {
      await mongoose.connect(uri);
      console.log("Connected to MongoDB");
      return;
    } catch (err) {
      console.log(`MongoDB connection attempt ${i + 1}/${maxRetries} failed, retrying...`);
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  throw new Error("Could not connect to MongoDB");
}
