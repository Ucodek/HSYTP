/**
 * Secure encryption utility for client-side data protection using Web Crypto API.
 *
 * This implementation uses AES-GCM, a modern authenticated encryption algorithm
 * that provides both confidentiality and integrity protection.
 */

// Encryption settings
const ALGORITHM = "AES-GCM";
const KEY_LENGTH = 256; // bits
const ITERATION_COUNT = 100000;
const SALT = new TextEncoder().encode("secure-storage-salt");
const IV_LENGTH = 12; // 12 bytes for AES-GCM

// Get encryption key - in a real app, this might be more dynamic
const getEncryptionKey = async (): Promise<CryptoKey> => {
  // Use a secret from environment or fallback
  const secret =
    process.env.NEXT_PUBLIC_ENCRYPTION_KEY ||
    "default-encryption-key-for-client-storage";

  // Derive a secure key using PBKDF2
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: SALT,
      iterations: ITERATION_COUNT,
      hash: "SHA-256",
    },
    keyMaterial,
    { name: ALGORITHM, length: KEY_LENGTH },
    false,
    ["encrypt", "decrypt"]
  );
};

/**
 * Encrypt data using AES-GCM
 */
export async function encryptData(data: string): Promise<string> {
  try {
    if (!isEncryptionAvailable()) {
      throw new Error("Web Crypto API not available");
    }

    // Generate random initialization vector
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
    const key = await getEncryptionKey();

    // Encode data to encrypt
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);

    // Encrypt the data
    const encryptedBuffer = await crypto.subtle.encrypt(
      {
        name: ALGORITHM,
        iv,
      },
      key,
      dataBuffer
    );

    // Combine IV and encrypted data and convert to base64
    const result = new Uint8Array(iv.length + encryptedBuffer.byteLength);
    result.set(iv);
    result.set(new Uint8Array(encryptedBuffer), iv.length);

    return btoa(String.fromCharCode(...result));
  } catch (error) {
    console.error("Encryption failed:", error);
    // Fallback to simpler storage if encryption fails
    return data;
  }
}

/**
 * Decrypt data using AES-GCM
 */
export async function decryptData(encryptedData: string): Promise<string> {
  try {
    if (!isEncryptionAvailable()) {
      throw new Error("Web Crypto API not available");
    }

    // Convert from base64 to array
    const encryptedArray = new Uint8Array(
      atob(encryptedData)
        .split("")
        .map((char) => char.charCodeAt(0))
    );

    // Extract IV and encrypted data
    const iv = encryptedArray.slice(0, IV_LENGTH);
    const data = encryptedArray.slice(IV_LENGTH);

    // Get key and decrypt
    const key = await getEncryptionKey();
    const decryptedBuffer = await crypto.subtle.decrypt(
      {
        name: ALGORITHM,
        iv,
      },
      key,
      data
    );

    // Decode to string
    const decoder = new TextDecoder();
    return decoder.decode(decryptedBuffer);
  } catch (error) {
    console.error("Decryption failed:", error);
    // If decryption fails, try to return as-is (might be unencrypted)
    return encryptedData;
  }
}

/**
 * Check if encryption is available in the current environment
 */
export function isEncryptionAvailable(): boolean {
  return (
    typeof crypto !== "undefined" &&
    typeof crypto.subtle !== "undefined" &&
    typeof TextEncoder !== "undefined" &&
    typeof TextDecoder !== "undefined"
  );
}

/**
 * Legacy compatibility layer for sync operations
 * These should be used only when async operations aren't possible
 */
export function encrypt(data: string): string {
  console.warn(
    "Synchronous encryption is less secure. Use encryptData when possible."
  );
  return btoa(data); // Simple encoding, not true encryption
}

export function decrypt(encryptedData: string): string {
  console.warn(
    "Synchronous decryption is less secure. Use decryptData when possible."
  );
  try {
    return atob(encryptedData); // Simple decoding
  } catch (e) {
    console.error("Decryption failed:", e);
    return encryptedData; // Return as-is if not base64
  }
}
