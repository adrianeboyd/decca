<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="ISO-8859-1" omit-xml-declaration="yes"/>

<!-- 
 DECCA infomation:

 Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
 Contact: decca@ling.osu.edu
 URL: http://decca.osu.edu
 License: GNU GPL (http://decca.osu.edu/software/license.html)
-->

<!-- simply match elements and apply templates for a number of entities -->

<xsl:template match = "s">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match = "graph">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="terminals">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="nonterminals">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="nt">

<!-- the two parameters tell us if the template has been called from another template or
     not (identity) and if there are unary categories above it (category) -->
<xsl:param name="category">null</xsl:param>
<xsl:param name="identity">null</xsl:param>

<!-- ntcat will either be the current category or a concatenation of previous categories      
with this one -->
<xsl:variable name="ntcat">
  <xsl:choose>
    <xsl:when test="$category='null'">
      <xsl:value-of select="@cat"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="concat($category,'/',@cat)"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:variable>

  <!-- We print out the category at the beginning of a line before its yield -->

  <xsl:choose>
    <!-- identity=null means this is the beginning of a yield,
         and the other condition checks that it is not a unary branch 
         (unary branches will get printed when they are no longer unary or they hit
          terminal element) -->
    <xsl:when test="$identity='null' and not(edge[position()=1 and position()=last()])">
      <xsl:value-of select="$ntcat"/><xsl:text>	</xsl:text>
    </xsl:when>
    <!-- we also print when a unary branch dominates a terminal -->
    <xsl:when test="$identity='null' and edge[position()=1 and position()=last()] and edge/@idref=../../terminals/t/@id">
      <xsl:value-of select="$ntcat"/><xsl:text>	</xsl:text>
    </xsl:when>
  </xsl:choose>

  <!-- follow the paths of all of a nt's edges in order to eventually get the 
       terminal span -->
  <xsl:for-each select="edge">
    <xsl:variable name="edgeid" select="@idref"/>

    <xsl:choose>

      <!-- the edge is a nonterminal -->
      <xsl:when test="$edgeid=../../nt/@id">
        <xsl:choose>

          <!-- the edge has no siblings:  it is a unary branch -->
          <xsl:when test="position()=1 and position()=last()">
            <xsl:choose>

              <!-- if we are at the beginning, we make a call to apply-templates with                           no parameter for identity, so that the category will get printed out 
                   when no longer unary -->
              <xsl:when test="$identity='null'">
                <xsl:apply-templates select="../../nt[@id=$edgeid]">
                  <xsl:with-param name="category" select="$ntcat"/>
                </xsl:apply-templates>
              </xsl:when>

              <!-- if we in the middle of another nt's yield, we do not want to print
                   the category, so we ensure that "identity" is non-null -->
              <xsl:otherwise>
                <xsl:apply-templates select="../../nt[@id=$edgeid]">
                  <xsl:with-param name="category" select="$ntcat"/>
                  <xsl:with-param name="identity" select="$edgeid"/>
                </xsl:apply-templates>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>

          <!-- the edge has siblings and so is not unary -->
          <xsl:otherwise>
            <xsl:apply-templates select="../../nt[@id=$edgeid]">
              <xsl:with-param name="identity" select="$edgeid"/>
            </xsl:apply-templates>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <!-- the edge is a terminal -->
      <xsl:when test="$edgeid=../../../terminals/t/@id">
        <xsl:apply-templates select="../../../terminals/t[@id=$edgeid]">
          <xsl:with-param name="identity" select="$edgeid"/>
        </xsl:apply-templates>
      </xsl:when>

    </xsl:choose>

  </xsl:for-each>

</xsl:template>

<!-- terminal nodes -->

<xsl:template match="t">
<xsl:param name="identity">null</xsl:param>

  <!-- only get the id and word if the template was called from another template -->
  <xsl:if test="$identity=@id">
    <xsl:value-of select="@id"/><xsl:text>	</xsl:text>
    <xsl:value-of select="@word"/><xsl:text>	</xsl:text>
  </xsl:if>

</xsl:template>

</xsl:stylesheet>
