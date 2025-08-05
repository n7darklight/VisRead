-- VisRead Database Schema
-- Supabase (PostgreSQL)

-- ####################################################################
-- Table for storing user account information.
-- ####################################################################

CREATE TABLE visread_users (
    -- Unique identifier for each user, automatically generated.
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Username for the user, must be unique.
    username TEXT UNIQUE NOT NULL,

    -- Hashed password for the user.
    password TEXT NOT NULL,

    -- Timestamp of when the user account was created.
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ####################################################################
-- Table for storing books, chapters, and generated image data.
-- ####################################################################

CREATE TABLE visread_books (
    -- Unique identifier for each book, automatically generated.
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Foreign key linking to the user who created the book.
    user_id UUID REFERENCES visread_users(id) ON DELETE CASCADE,

    -- The title of the book.
    title TEXT NOT NULL,

    -- The author of the book (optional).
    author TEXT,

    -- An array of text, where each element is a chapter/paragraph.
    chapters TEXT[],

    -- A JSON object to store image URLs.
    -- The key is the chapter index (as a string, e.g., "0", "1"),
    -- and the value is the URL to the generated image.
    -- Example: {"0": "https://...", "1": "https://..."}
    images JSONB DEFAULT '{}'::jsonb,

    -- A text field to store the AI-generated consistency guide for the book's art style and characters.
    style_guide TEXT,

    -- Timestamp of when the book was created.
    created_at TIMESTAMPTZ DEFAULT now()
);
