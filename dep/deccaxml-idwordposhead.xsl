<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="text" indent="no" encoding="utf-8" omit-xml-declaration="yes"/>

<xsl:template match="sentence">
  <xsl:variable name="sentenceid" select="@id"/>
  <xsl:for-each select="word">
    <xsl:text>s</xsl:text>
    <xsl:value-of select="$sentenceid"/>
    <xsl:text>_</xsl:text>
    <xsl:value-of select="@id"/><xsl:text>	</xsl:text>
    <xsl:value-of select="@form"/><xsl:text>	</xsl:text>
    <xsl:value-of select="@postag"/><xsl:text>	</xsl:text>
    <xsl:for-each select="head">
      <xsl:value-of select="@deprel"/><xsl:text> </xsl:text>
    </xsl:for-each>
    <xsl:text>	</xsl:text>
    <xsl:value-of select="@form"/><xsl:text>	</xsl:text>
    <xsl:text>
    </xsl:text>
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
