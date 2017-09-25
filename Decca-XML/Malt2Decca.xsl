<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"> 
<!--xmlns="http://decca.osu.edu">-->

<xsl:output method="xml" indent="yes" encoding="utf-8"/>

<xsl:template match="treebank">
  <treebank xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://decca.osu.edu/schema/Decca-XML.xsd">
    <xsl:attribute name="id">
      <xsl:value-of select="@id"/>
    </xsl:attribute>
    <xsl:apply-templates/>
  </treebank>
</xsl:template>

<xsl:template match="body|sentence">
  <xsl:copy>
    <xsl:copy-of select="@*"/>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>

<xsl:template match="head">
  <header>
  <xsl:apply-templates/>
  </header>
</xsl:template>

<xsl:template match="annotation">
  <xsl:copy>
    <xsl:copy-of select="*"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="word">
  <xsl:copy>
    <xsl:attribute name="id">
      <xsl:value-of select="@id"/>
    </xsl:attribute>
    <xsl:attribute name="form">
      <xsl:value-of select="@form"/>
    </xsl:attribute>
    <xsl:if test="@lemma">
      <xsl:attribute name="lemma">
        <xsl:value-of select="@lemma"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="@cpostag">
      <xsl:attribute name="cpostag">
        <xsl:value-of select="@cpostag"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="@postag">
      <xsl:attribute name="postag">
        <xsl:value-of select="@postag"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="@chunk">
      <xsl:attribute name="chunk">
        <xsl:value-of select="@chunk"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="@head">
      <xsl:element name="head">
        <xsl:attribute name="id">
          <xsl:value-of select="@head"/>
        </xsl:attribute>
        <xsl:attribute name="deprel">
          <xsl:value-of select="@deprel"/>
        </xsl:attribute>
      </xsl:element>
    </xsl:if>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>
