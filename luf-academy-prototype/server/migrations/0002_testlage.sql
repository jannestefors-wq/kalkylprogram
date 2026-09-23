-- LUF Academy. Min ledarskapsresa. Prototyp 002.
-- Endast additiv. Testläge per deltagare, så att en testperson kan flyttas
-- genom resan utan att verklig tid går. Används bara när servern körs som
-- prototyp. I produktion ignoreras kolumnen.
ALTER TABLE lr_enrollment ADD COLUMN test_step TEXT;
