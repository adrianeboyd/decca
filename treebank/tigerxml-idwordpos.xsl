<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- 
 DECCA infomation:

 Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
 Contact: decca@ling.osu.edu
 URL: http://decca.osu.edu
 License: GNU GPL (http://decca.osu.edu/software/license.html)
-->

<!-- extract the id, word, and pos attributes from each terminal -->

<xsl:output method="text" encoding="ISO-8859-1" omit-xml-declaration="yes" indent="no" />

<xsl:template match="t">
  <xsl:value-of select="@id"/><xsl:text>	</xsl:text>
  <xsl:value-of select="@word"/><xsl:text>	</xsl:text>
  <xsl:value-of select="@pos"/>
</xsl:template>

</xsl:stylesheet>
