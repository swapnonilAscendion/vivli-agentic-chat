import logging
from typing import List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk"""
    text: str
    chunk_index: int
    source: str
    source_url: str = None
    metadata: dict = None


class TextChunker:
    """Split documents into overlapping chunks"""

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
        separator: str = "\n\n",
    ):
        """
        Initialize text chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Number of characters to overlap between chunks
            separator: Primary separator for chunking (e.g., paragraph breaks)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separator = separator

    def chunk_text(
        self,
        text: str,
        source: str,
        source_url: str = None,
        metadata: dict = None,
    ) -> List[Chunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            source: Source document name
            source_url: URL or path to source
            metadata: Additional metadata

        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []

        # Clean text
        text = text.strip()

        # Try to split by paragraphs first
        paragraphs = text.split(self.separator)

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk_size, save current chunk
            if (
                current_chunk
                and len(current_chunk) + len(paragraph) > self.chunk_size
            ):
                chunks.append(
                    Chunk(
                        text=current_chunk.strip(),
                        chunk_index=chunk_index,
                        source=source,
                        source_url=source_url,
                        metadata=metadata,
                    )
                )
                chunk_index += 1

                # Start new chunk with overlap
                # Keep last `overlap` chars from previous chunk
                overlap_text = current_chunk[-self.overlap :] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + self.separator + paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += self.separator + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                Chunk(
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    source=source,
                    source_url=source_url,
                    metadata=metadata,
                )
            )

        logger.info(
            f"Chunked '{source}' into {len(chunks)} chunks "
            f"(avg size: {len(text) // max(len(chunks), 1)} chars)"
        )
        return chunks

    def chunk_document(
        self,
        document: dict,
    ) -> List[Chunk]:
        """
        Chunk a document dictionary.

        Document should have:
        - content: Main text content
        - source: Source name
        - source_url: Optional URL
        - metadata: Optional dict

        Args:
            document: Document dict

        Returns:
            List of Chunk objects
        """
        return self.chunk_text(
            text=document.get("content", ""),
            source=document.get("source", "unknown"),
            source_url=document.get("source_url"),
            metadata=document.get("metadata"),
        )
