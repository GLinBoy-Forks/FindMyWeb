import { Location } from "./FindMyWeb";

const dateTimeFormatter = new Intl.DateTimeFormat([], {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

export async function locationDateString(location: Location): Promise<string> {
  if (!location.timestamp) {
    return "No timestamp";
  }
  // Append 'Z' so ts knows this is a UTC date
  return dateTimeFormatter.format(new Date(location.timestamp + "Z"));
}
