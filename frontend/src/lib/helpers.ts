import { type Location } from "./FindMyWeb.ts";

const dateTimeFormatter = new Intl.DateTimeFormat([], {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

const base64regex =
  /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;

export async function locationDate(location: Location): Promise<Date | null> {
  if (!location.timestamp) {
    return null;
  }
  // Append 'Z' so ts knows this is a UTC date
  return new Date(location.timestamp + "Z");
}

export async function locationDateString(location: Location): Promise<string> {
  const date = await locationDate(location);
  if (!date) {
    return "No timestamp";
  }
  return dateTimeFormatter.format(date);
}

export async function isBase64(str: string) {
  return str.match(base64regex);
}
