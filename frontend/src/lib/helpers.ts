import { Location } from "./FindMyWeb";

const dateTimeFormatter = new Intl.DateTimeFormat([], {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

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
