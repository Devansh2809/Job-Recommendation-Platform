from .heading_detector import is_heading

def split_into_sections(text: str) -> dict:
    """
    Split resume text into sections based on detected headings.
    Returns dict of {heading_text: content}.
    
    Improved to handle multi-line section content properly.
    """
    sections = {}
    current_heading = "header"  # Pre-heading content (name, contact, etc.)
    current_content = []
    
    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        # Check if this line is a heading
        if is_heading(line):
            # Save previous section if it has content
            if current_content:
                sections[current_heading] = "\n".join(current_content).strip()
            
            # Start new section
            current_heading = line.strip()
            current_content = []
        else:
            # Add line to current section
            current_content.append(line)
    
    # Don't forget the last section
    if current_content:
        sections[current_heading] = "\n".join(current_content).strip()
    
    # Filter out empty sections
    return {k: v for k, v in sections.items() if v}