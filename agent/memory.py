from .llm import summary_llm

class ShortTermManager:
    def __init__(self, max_tail=6, chunk_size=4):
        """
        max_tail: The number of recent RAW messages to keep perfectly intact (6 = last 3 turns).
        chunk_size: How many old raw messages must accumulate in the middle before we compress them.
        """
        self.max_tail = max_tail
        self.chunk_size = chunk_size

    def summarize_chunk(self, chunk):
        """A fast, cheap background LLM call to compress older memory."""
        print("\n🗜️  [MEMORY THREAD] Compressing older actions to save tokens...")
        
        transcript = ""
        for msg in chunk:
            transcript += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
        system_prompt = """You are a memory compression node for an autonomous agent.
        Summarize the following sequence of past actions and observations. 
        Keep it highly concise (2-3 sentences). Focus ONLY on:
        1. What tools were used.
        2. What crucial data was discovered (facts, URLs, company details).
        3. What errors occurred (so the agent doesn't repeat them)."""
        
        try:
            response = summary_llm.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"TRANSCRIPT TO SUMMARIZE:\n{transcript}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Memory compression failed: {e}")
            return "Summary unavailable."

    def prune_messages(self, messages):
        """
        Implements the Rolling Summary Buffer.
        Replaces chunks of raw middle messages with compressed summary nodes.
        """
        # If the conversation hasn't grown past our Head + Tail threshold, do nothing.
        if len(messages) <= 2 + self.max_tail:
            return messages

        # 1. Lock the Head
        head = messages[:2]
        
        # 2. Extract the working body (everything between the Head and the Tail)
        working_body = messages[2:-self.max_tail]
        
        # 3. Lock the Tail
        tail = messages[-self.max_tail:]
        
        # 4. Separate existing Summaries from Raw Messages in the working body
        summary_tag = "🕒 MEMORY COMPRESSION:"
        
        summaries = [m for m in working_body if m["role"] == "system" and m["content"].startswith(summary_tag)]
        raws = [m for m in working_body if not (m["role"] == "system" and m["content"].startswith(summary_tag))]
        
        # 5. If we have accumulated enough Raw messages, compress them!
        if len(raws) >= self.chunk_size:
            chunk_to_summarize = raws[:self.chunk_size]
            leftover_raws = raws[self.chunk_size:]
            
            summary_text = self.summarize_chunk(chunk_to_summarize)
            new_summary = {"role": "system", "content": f"{summary_tag}\n{summary_text}"}
            
            # Append the new summary block to the existing summary blocks
            summaries.append(new_summary)
            
            # Reconstruct the working body
            working_body = summaries + leftover_raws
            
        # Stitch the entire prompt back together and return it
        return head + working_body + tail