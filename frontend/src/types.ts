export interface Template {
    id: string; // Backend returns int, but we might want to cast to string or handle as int. Let's handle generic ID.
    title: string;
    type: "IMAGE" | "VIDEO";
    thumbnail: string;
    source_url?: string;
    cost: number;
}
