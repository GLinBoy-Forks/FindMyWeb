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

const base64Bytes28regex = /^[0-9a-zA-Z+/]{38}==$/;
const base64Bytes32regex = /^[0-9a-zA-Z+/]{43}=$/;

const hexBytes28regex = /^[0-9a-fA-F]{56}$/;
const hexBytes32regex = /^[0-9a-fA-F]{64}$/;

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

export async function isBytes28Base64(str: string) {
  return str.match(base64Bytes28regex);
}

export async function isBytes32Base64(str: string) {
  return str.match(base64Bytes32regex);
}

export async function isBytes28Hex(str: string) {
  return str.match(hexBytes28regex);
}

export async function isBytes32Hex(str: string) {
  return str.match(hexBytes32regex);
}

export function hexToBase64(str: string) {
  var bytes = "";
  for (var i = 0; i < str.length; i += 2) {
    bytes += String.fromCharCode(parseInt(str.slice(i, i + 2), 16));
  }
  return btoa(bytes);
}

export function plistToJson(plist: Element): any {
  switch (plist.nodeName) {
    case "plist":
      if (plist.children.length != 1)
        throw new Error("Invalid plist: <plist> has multiple children");
      return plistToJson(plist.children[0]);
    case "dict":
      var result = new Map();
      for (let i = 0; i < plist.children.length; i += 2) {
        const key = plist.children[i];
        if (key.nodeName != "key" || key.children.length != 0)
          throw new Error(`Invalid plist: <dict> has invalid key node: ${key}`);

        const value = plistToJson(plist.children[i + 1]);
        result.set(key.textContent, value);
      }
      return result;
    case "array":
      return Array.from(plist.children).map((child) => plistToJson(child));
  }

  if (plist.children.length != 0)
    throw new Error(
      `Invalid plist: <${plist.nodeName}> node shouldn't contain children: ${plist}`,
    );

  switch (plist.nodeName) {
    case "date":
      return new Date(plist.textContent);
    case "integer":
      return parseInt(plist.textContent);
    case "string":
      return plist.textContent;
    case "data":
      return plist.textContent
        .replaceAll("\t", "")
        .replaceAll("\n", "")
        .replaceAll(" ", "");
    case "false":
      return false;
    case "true":
      return true;
    default:
      throw new Error("Invalid plist: Unrecognized node: " + plist.nodeName);
  }
}

export function readXMLFile(file: File) {
  const reader = new FileReader();
  const parser = new DOMParser();

  reader.readAsText(file);

  return new Promise((resolve, reject) => {
    reader.onload = () => {
      if (!reader.result || reader.result instanceof ArrayBuffer)
        throw new Error("Reading file failed");
      const xml = parser.parseFromString(reader.result, "application/xml");

      if (xml.documentElement.nodeName == "parsererror") {
        reject(xml.documentElement.textContent);
      }

      resolve(xml);
    };
    reader.onerror = () => reject("Error reading file");
  });
}
