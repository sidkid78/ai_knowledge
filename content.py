import re
import autogen

class ContentCreationAgent(autogen.Agent):
    def __init__(self, content_type, target_audience, tone, outline):
        """
        Initialize the agent with:
        content_type: The nature of the content (technical, creative, or marketing).
        target_audience: The intended audience for the content.
        tone: The desired tone (e.g., formal, casual, enthusiastic).
        outline: A dictionary or list containing key points or a structured outline.
        """
        super().__init__()
        self.content_type = content_type 
        self.target_audience = target_audience
        self.tone = tone 
        self.outline = outline 
        self.draft = ""

    def parse_input(self):
        """Ensure that inputs are in the correct format and validate key elements."""
        # Convert outline into a string or a structure acceptable to the drafting method
        if isinstance(self.outline, list):
            parsed_outline = "\n".join(self.outline)
        elif isinstance(self.outline, dict):
            parsed_outline = "\n".join([f"{k}: {v}" for k, v in self.outline.items()])
        else:
            parsed_outline = str(self.outline)
        return parsed_outline

    def draft_content(self):
        """Generate a first-draft content based on the outline provided."""
        parsed_outline = self.parse_input()

        # Use autogen's content-generation method
        prompt = (f"Generate a {self.content_type} piece for an audience of {self.target_audience}. "
                  f"The tone should be {self.tone}. Please use the following outline or key points:\n"
                  f"{parsed_outline}\n\nDraft the content accordingly.")
    
        # Assuming autogen.Generator is provided by the framework for text generation
        self.draft = autogen.Generator.generate(prompt)
        return self.draft

    def check_and_adjust_tone(self):
        """Analyze and adjust the tone of the content to match the target specification."""
        # For demonstration, a simple check might be to ensure certain tone keywords are present.
        # More advanced implementations could involve sentiment analysis APIs.
        tone_keywords = {
            'formal': ['Dear', 'Sincerely', 'Regards'],
            'casual': ['Hey', 'Cheers', 'Hi'],
            'enthusiastic': ['exciting', 'fantastic', 'amazing']
        }
        keywords = tone_keywords.get(self.tone.lower(), [])
        if keywords:
            matches = sum(1 for word in keywords if re.search(rf'\b{word}\b', self.draft, re.IGNORECASE))
            # If less than a certain threshold, append a note to adjust the tone.
            if matches < 1:
                self.draft += f"\n\n(Note: Please ensure the tone reflects a {self.tone} style by incorporating elements such as: {', '.join(keywords)}.)"
        return self.draft

    def revise_content(self):
        """Revise the draft content for clarity and coherence using autogen tools."""
        # Another prompt can be used to refine and edit the draft.
        prompt = (f"Please review and revise the following content for clarity, coherence, and tone alignment with "
                  f"an audience of {self.target_audience} using a {self.tone} tone. Make improvements to the structure as needed:\n\n"
                  f"{self.draft}")
        revised_content = autogen.Generator.generate(prompt)
        self.draft = revised_content
        return self.draft

def run(self):
    """Execute the complete process: drafting, tone alignment, and revision."""
    print("Drafting content...")
    self.draft_content()
    print("Checking and adjusting tone...")
    self.check_and_adjust_tone()
    print("Revising content...")
    final_output = self.revise_content()
    return final_output

if __name__ == "__main__":
    # inpit parameters for the agent
    content_type = "blog post"
    target_audience = "tech enthusiasts"
    tone = "enthusiastic"
    outline = [ "Introduction: Introduce the topic of AI innovations.", "Body: Discuss recent trends, challenges, and breakthroughs.", "Conclusion: Summarize future prospects of AI." ]
