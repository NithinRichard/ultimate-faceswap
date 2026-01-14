const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchWithAuth(url: string, token: string | null, options: RequestInit = {}) {
    const headers = {
        ...options.headers,
        "Authorization": token ? `Bearer ${token}` : "",
    };

    const res = await fetch(`${API_URL}${url}`, {
        ...options,
        headers,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(error.detail || `API request failed with status ${res.status}`);
    }

    return res.json();
}

export async function uploadFile(file: File, token: string) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_URL}/swaps/upload`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
        body: formData,
    });

    if (!res.ok) {
        throw new Error("File upload failed");
    }

    return res.json();
}
