import { access, copyFile } from "node:fs/promises";
import { constants } from "node:fs";

async function copyEnvTemplate(): Promise<void> {
  try {
    await access(".env", constants.F_OK);
  } catch {
    await copyFile(".env.example", ".env");
  }
}

void copyEnvTemplate();
